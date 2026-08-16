#!/usr/bin/evn python3
import logging
from datetime import datetime
from time import time

import discord
from discord.ext import tasks

from config import *
from discord_logger import DiscordLogger
from offers_storage import OffersStorage
from scrapers.rental_offer import RentalOffer
from scrapers_manager import create_scrapers, fetch_latest_offers
from datetime import datetime
import asyncio

def get_current_daytime() -> bool: return datetime.now().hour in range(6, 22)


def _clip(value, limit: int) -> str:
    """Clip untrusted offer text to a Discord field limit (safe fallback for None)."""
    text = "" if value is None else str(value)
    if len(text) > limit:
        text = text[:limit]
    return text


client = discord.Client(intents=discord.Intents.default())
daytime = get_current_daytime()
interval_time = config.refresh_interval_daytime_minutes if daytime else config.refresh_interval_nighttime_minutes

scrapers = create_scrapers(config.dispositions)

@client.event
async def on_ready():
    global channel, storage

    dev_channel = client.get_channel(config.discord.dev_channel)
    channel = client.get_channel(config.discord.offers_channel)
    storage = OffersStorage(config.found_offers_file)

    if not config.debug:
        discord_error_logger = DiscordLogger(client, dev_channel, logging.ERROR)
        logging.getLogger().addHandler(discord_error_logger)
    else:
        logging.info("Discord logger is inactive in debug mode")

    logging.info("Available scrapers: " + ", ".join([s.name for s in scrapers]))

    logging.info("Fetching latest offers every {} minutes".format(interval_time))

    process_latest_offers.start()

@tasks.loop(minutes=interval_time)
async def process_latest_offers():
    logging.info("Fetching offers")

    new_offers: list[RentalOffer] = []
    for offer in fetch_latest_offers(scrapers):
        if not storage.contains(offer):
            new_offers.append(offer)

    first_time = storage.first_time
    storage.save_offers(new_offers)

    logging.info("Offers fetched (new: {})".format(len(new_offers)))

    if not first_time:
        def chunk_offers(offers, size):
            for i in range(0, len(offers), size):
                yield offers[i:i + size]

        for offer_batch in chunk_offers(new_offers, config.embed_batch_size):
            embeds = []

            for offer in offer_batch:
                try:
                    color = offer.scraper.color if isinstance(offer.scraper.color, int) else 0xFFFFFF
                    embed = discord.Embed(
                        title=_clip(offer.title, 256),
                        url=offer.link if isinstance(offer.link, str) else None,
                        description=_clip(offer.location, 4096),
                        timestamp=datetime.utcnow(),
                        color=color
                    )
                    embed.add_field(name="Cena", value=_clip(str(offer.price) + " Kč", 1024))
                    if offer.scraper.name:
                        embed.set_author(name=_clip(offer.scraper.name, 256), icon_url=offer.scraper.logo_url)
                    if offer.image_url:
                        embed.set_image(url=offer.image_url)

                    embeds.append(embed)
                except Exception as e:
                    logging.warning(f"Skipping malformed offer {getattr(offer, 'link', '?')}: {e}")
                    continue

            if embeds:
                await retry_until_successful_send(channel, embeds)
                await asyncio.sleep(1.5)
    else:
        logging.info("No previous offers, first fetch is running silently")

    global daytime, interval_time
    if daytime != get_current_daytime():  # Pokud stary daytime neodpovida novemu

        daytime = not daytime  # Zneguj daytime (podle podminky se zmenil)

        interval_time = config.refresh_interval_daytime_minutes if daytime else config.refresh_interval_nighttime_minutes

        logging.info("Fetching latest offers every {} minutes".format(interval_time))
        process_latest_offers.change_interval(minutes=interval_time)

    await retry_until_successful_edit(channel, f"Last update <t:{int(time())}:R>")


def _is_permanent_http_error(e: discord.errors.HTTPException) -> bool:
    """Client errors (4xx) mean Discord will keep rejecting this payload, so
    retrying forever would hang the scheduled task (DoS). Server errors (5xx)
    and unknown statuses are treated as transient."""
    status = getattr(e, "status", None)
    return status is not None and 400 <= status < 500


async def retry_until_successful_send(channel: discord.TextChannel, embeds: list[discord.Embed], delay: float = 5.0, max_attempts: int = 5):
    """Retry sending a message with embeds until it succeeds.

    Transient server errors (5xx) are retried up to ``max_attempts`` times.
    Permanent client errors (4xx, e.g. a malformed/untrusted payload rejected
    by Discord) are logged and abandoned instead of retried indefinitely.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            await channel.send(embeds=embeds)
            logging.info("Embeds successfully sent.")
            return
        except discord.errors.DiscordServerError as e:
            logging.warning(f"Discord server error while sending embeds (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay:.1f}s.")
        except discord.errors.HTTPException as e:
            if _is_permanent_http_error(e):
                logging.error(f"Permanent client error while sending embeds, not retrying: {e}")
                return
            logging.warning(f"HTTPException while sending embeds (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay:.1f}s.")
        except Exception as e:
            logging.exception(f"Unexpected error while sending embeds: {e}. Retrying in {delay:.1f}s.")
            raise e
        if attempt < max_attempts:
            await asyncio.sleep(delay)
    logging.error(f"Failed to send embeds after {max_attempts} attempts. Skipping batch.")


async def retry_until_successful_edit(channel: discord.TextChannel, topic: str, delay: float = 5.0, max_attempts: int = 5):
    """Retry editing a channel topic until it succeeds.

    Transient server errors (5xx) are retried up to ``max_attempts`` times.
    Permanent client errors (4xx) are logged and abandoned instead of
    retried indefinitely to avoid hanging the scheduled task.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            await channel.edit(topic=topic)
            logging.info(f"Channel topic successfully updated to: {topic}")
            return
        except discord.errors.DiscordServerError as e:
            logging.warning(f"Discord server error while editing topic (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay:.1f}s.")
        except discord.errors.HTTPException as e:
            if _is_permanent_http_error(e):
                logging.error(f"Permanent client error while editing topic, not retrying: {e}")
                return
            logging.warning(f"HTTPException while editing topic (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay:.1f}s.")
        except Exception as e:
            logging.exception(f"Unexpected error while editing channel topic: {e}. Retrying in {delay:.1f}s.")
            raise e
        if attempt < max_attempts:
            await asyncio.sleep(delay)
    logging.error(f"Failed to edit channel topic after {max_attempts} attempts. Skipping update.")

if __name__ == "__main__":
    logging.basicConfig(
        level=(logging.DEBUG if config.debug else logging.INFO),
        format='%(asctime)s - [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.debug("Running in debug mode")

    client.run(config.discord.token, log_level=logging.INFO)
