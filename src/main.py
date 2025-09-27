#!/usr/bin/evn python3
import logging
from datetime import datetime
from time import time
import asyncio

from discord.ext import tasks

from config import *
from bot_wrapper import create_bot, DiscordBotWrapper
from offers_storage import OffersStorage
from scrapers.rental_offer import RentalOffer
from scrapers_manager import create_scrapers, fetch_latest_offers

def get_current_daytime() -> bool: return datetime.now().hour in range(6, 22)


# Global variables
bot = create_bot()
storage = None
daytime = get_current_daytime()
interval_time = config.refresh_interval_daytime_minutes if daytime else config.refresh_interval_nighttime_minutes
scrapers = create_scrapers(config.dispositions)

async def initialize_bot():
    global storage
    
    await bot.initialize()
    storage = OffersStorage(config.found_offers_file)
    
    bot.setup_error_logging()

    logging.info("Available scrapers: " + ", ".join([s.name for s in scrapers]))
    logging.info("Fetching latest offers every {} minutes".format(interval_time))

    if isinstance(bot, DiscordBotWrapper):
        process_latest_offers.start()
    else:
        await run_telegram_loop()

# Discord-specific event handling
if isinstance(bot, DiscordBotWrapper):
    @bot.client.event
    async def on_ready():
        await initialize_bot()

async def fetch_and_process_offers():
    logging.info("Fetching offers")

    new_offers: list[RentalOffer] = []
    for offer in fetch_latest_offers(scrapers):
        if not storage.contains(offer):
            new_offers.append(offer)
    
    print(new_offers)

    first_time = storage.first_time
    storage.save_offers(new_offers)

    logging.info("Offers fetched (new: {})".format(len(new_offers)))

    if not first_time:
        await bot.send_offers(new_offers)
    else:
        logging.info("No previous offers, first fetch is running silently")

    global daytime, interval_time
    if daytime != get_current_daytime():  # Pokud stary daytime neodpovida novemu

        daytime = not daytime  # Zneguj daytime (podle podminky se zmenil)

        interval_time = config.refresh_interval_daytime_minutes if daytime else config.refresh_interval_nighttime_minutes

        logging.info("Fetching latest offers every {} minutes".format(interval_time))
        
        if isinstance(bot, DiscordBotWrapper):
            process_latest_offers.change_interval(minutes=interval_time)

    if isinstance(bot, DiscordBotWrapper):
        await bot.update_status(f"Last update <t:{int(time())}:R>")

@tasks.loop(minutes=interval_time)
async def process_latest_offers():
    """Discord-specific wrapper for the core logic"""
    await fetch_and_process_offers()

async def run_telegram_loop():
    """Telegram-specific loop for processing offers"""
    while True:
        try:
            await fetch_and_process_offers()
            await asyncio.sleep(interval_time * 60)  # Convert minutes to seconds
        except Exception as e:
            logging.exception(f"Error in Telegram loop: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying




async def main():
    """Main function for Telegram bot"""
    await initialize_bot()

if __name__ == "__main__":
    logging.basicConfig(
        level=(logging.DEBUG if config.debug else logging.INFO),
        format='%(asctime)s - [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.debug("Running in debug mode")
    
    if isinstance(bot, DiscordBotWrapper):
        bot.run()
    else:
        # Run Telegram bot
        asyncio.run(main())
