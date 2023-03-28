#!/usr/bin/evn python3
import logging
import discord
from typing import List
from config import *
from discord.ext import tasks
from datetime import datetime
from time import time
from discord_logger import DiscordLogger
from offers_storage import OffersStorage
from scrapers_manager import create_scrapers, fetch_latest_offers
from scrapers.rental_offer import RentalOffer


def get_current_daytime() -> bool: return datetime.now().hour in range(6, 22)


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
    logging.log(config.info_debug_level, "Fetching offers")

    new_offers: List[RentalOffer] = []
    for offer in fetch_latest_offers(scrapers):
        if not config.found_offers_file.contains(offer):
            new_offers.append(offer)

    first_time = config.found_offers_file.first_time
    config.found_offers_file.save_offers(new_offers)

    logging.info("Offers fetched (new: {})".format(len(new_offers)))

    if not first_time:
        for offer in new_offers:
            embed = discord.Embed(
                title=offer.title,
                url=offer.link,
                description=offer.location,
                timestamp=datetime.utcnow(),
                color=offer.scraper.color
            )

            embed.add_field(name="Cena", value=str(offer.price) + " Kč")
            embed.set_author(name=offer.scraper.name, icon_url=offer.scraper.logo_url)
            embed.set_image(url=offer.image_url)

            await channel.send(embed=embed)
    else:
        logging.info("No previous offers, first fetch is running silently")

    global daytime, interval_time
    if daytime != get_current_daytime():  # Pokud stary daytime neodpovida novemu

        daytime = not daytime  # Zneguj daytime (podle podminky se zmenil)

        interval_time = config.refresh_interval_daytime_minutes if daytime else config.refresh_interval_nighttime_minutes

        logging.info("Fetching latest offers every {} minutes".format(interval_time))
        process_latest_offers.change_interval(minutes=interval_time)

    await channel.edit(topic="Last update {}".format("<t:{}:R>".format(int(time()))))


if __name__ == "__main__":
    logging.addLevelName(15, "INFO_DEBUG")

    logging.basicConfig(
        level=(config.info_debug_level if config.debug else logging.INFO),
        format='%(asctime)s - [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.log(config.debug, "Running in debug mode")

    client.run(config.discord.token)
