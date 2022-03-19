#!/usr/bin/evn python3
import logging
import discord
from typing import List
from config import *
from discord.ext import tasks
from datetime import datetime
from offers_storage import OffersStorage
from scraper import fetch_latest_offers
from scrapers.generic_apartment_rental_scraper import ApartmentRentalOffer


client = discord.Client()


@client.event
async def on_ready():
    global channel, storage

    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    channel = client.get_channel(DISCORD_CHANNEL)
    storage = OffersStorage(FOUND_OFFERS_FILE)

    logging.info("Fetching latest offers every " +
                 str(REFRESH_INTERVAL_MINUTES) + " minutes")
    process_latest_offers.start()


@tasks.loop(minutes=REFRESH_INTERVAL_MINUTES)
async def process_latest_offers():
    logging.info("Fetching offers")

    new_offers: List[ApartmentRentalOffer] = []
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
                description=offer.location +
                "\nCena " + str(offer.price) + " Kč",
                timestamp=datetime.now(),
                color=0xFF5733,
            )
            await channel.send(embed=embed)
    else:
        logging.info("No previous offers, first fetch is running silently")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
