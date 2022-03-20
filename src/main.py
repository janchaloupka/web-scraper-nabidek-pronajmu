#!/usr/bin/evn python3
import logging
import discord
from typing import List
from config import *
from discord.ext import tasks
from datetime import datetime
from discord_logger import DiscordLogger
from offers_storage import OffersStorage
from scrapers_manager import fetch_latest_offers, scrapers
from scrapers.rental_offer import RentalOffer


client = discord.Client()


@client.event
async def on_ready():
    global channel, storage

    dev_channel = client.get_channel(DISCORD_DEV_CHANNEL)
    channel = client.get_channel(DISCORD_OFFERS_CHANNEL)
    storage = OffersStorage(FOUND_OFFERS_FILE)

    if not DEBUG:
        discord_error_logger = DiscordLogger(client, dev_channel, logging.ERROR)
        logging.getLogger().addHandler(discord_error_logger)
    else:
        logging.info("Discord logger is inactive in debug mode")

    logging.info("Available scrapers: " + ", ".join([s.name for s in scrapers]))

    logging.info("Fetching latest offers every " +
                 str(REFRESH_INTERVAL_MINUTES) + " minutes")
    process_latest_offers.start()


@tasks.loop(minutes=REFRESH_INTERVAL_MINUTES)
async def process_latest_offers():
    logging.log(INFO_DEBUG, "Fetching offers")

    new_offers: List[RentalOffer] = []
    for offer in fetch_latest_offers():
        if not storage.contains(offer):
            new_offers.append(offer)

    first_time = storage.first_time
    storage.save_offers(new_offers)

    logging.info("Offers fetched (new: " + str(len(new_offers)) + ")")

    if not first_time:
        for offer in new_offers:
            embed = discord.Embed(
                title=offer.description,
                url=offer.link,
                description=offer.location,
                timestamp=datetime.now(),
                color=offer.scraper.color
            )

            embed.add_field(name="Cena", value=str(offer.price) + " Kč")
            embed.set_author(name=offer.scraper.name, icon_url=offer.scraper.logo_url)
            embed.set_image(url=offer.image_url)

            await channel.send(embed=embed)
    else:
        logging.info("No previous offers, first fetch is running silently")


if __name__ == "__main__":
    logging.addLevelName(15, "INFO_DEBUG")

    logging.basicConfig(
        level=(INFO_DEBUG if DEBUG else logging.INFO),
        format='%(asctime)s - [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.log(INFO_DEBUG, "Running in debug mode")

    client.logger = logging.getLogger("discord")
    client.run(DISCORD_TOKEN)
