import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from telegram import Bot as TelegramBot
import discord

from config import config
from discord_logger import DiscordLogger
from scrapers.rental_offer import RentalOffer


class BotInterface(ABC):    
    @abstractmethod
    async def initialize(self):
        pass
    
    @abstractmethod
    async def send_offers(self, offers: List[RentalOffer]):
        pass
    
    @abstractmethod
    async def update_status(self, message: str):
        pass
    
    @abstractmethod
    def setup_error_logging(self):
        pass
    
    @abstractmethod
    def run(self):
        pass


class DiscordBotWrapper(BotInterface):
    def __init__(self):
        if not config.discord.token:
            raise ValueError("DISCORD_TOKEN is required when BOT_TYPE is discord")
        if not config.discord.offers_channel:
            raise ValueError("DISCORD_OFFERS_CHANNEL is required when BOT_TYPE is discord")
        if not config.discord.dev_channel:
            raise ValueError("DISCORD_DEV_CHANNEL is required when BOT_TYPE is discord")
            
        self.client = discord.Client(intents=discord.Intents.default())
        self.channel = None
        self.dev_channel = None
        
    async def initialize(self):
        self.dev_channel = self.client.get_channel(config.discord.dev_channel)
        self.channel = self.client.get_channel(config.discord.offers_channel)
        
    def setup_error_logging(self):
        if not config.debug and self.dev_channel:
            discord_error_logger = DiscordLogger(self.client, self.dev_channel, logging.ERROR)
            logging.getLogger().addHandler(discord_error_logger)
        else:
            logging.info("Discord logger is inactive in debug mode")
            
    async def send_offers(self, offers: List[RentalOffer]):
        def chunk_offers(offers, size):
            for i in range(0, len(offers), size):
                yield offers[i:i + size]

        for offer_batch in chunk_offers(offers, config.embed_batch_size):
            embeds = []

            for offer in offer_batch:
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
                embeds.append(embed)

            await self._retry_until_successful_send(self.channel, embeds)
            await asyncio.sleep(1.5)

    async def update_status(self, message: str):
        await self._retry_until_successful_edit(self.channel, message)

    async def _retry_until_successful_send(self, channel: discord.TextChannel, embeds: List[discord.Embed], delay: float = 5.0):
        while True:
            try:
                await channel.send(embeds=embeds)
                logging.info("Embeds successfully sent.")
                return
            except discord.errors.DiscordServerError as e:
                logging.warning(f"Discord server error while sending embeds: {e}. Retrying in {delay:.1f}s.")
            except discord.errors.HTTPException as e:
                logging.warning(f"HTTPException while sending embeds: {e}. Retrying in {delay:.1f}s.")
            except Exception as e:
                logging.exception(f"Unexpected error while sending embeds: {e}. Retrying in {delay:.1f}s.")
                raise e
            await asyncio.sleep(delay)

    async def _retry_until_successful_edit(self, channel: discord.TextChannel, topic: str, delay: float = 5.0):
        while True:
            try:
                await channel.edit(topic=topic)
                logging.info(f"Channel topic successfully updated to: {topic}")
                return
            except discord.errors.DiscordServerError as e:
                logging.warning(f"Discord server error while editing topic: {e}. Retrying in {delay:.1f}s.")
            except discord.errors.HTTPException as e:
                logging.warning(f"HTTPException while editing topic: {e}. Retrying in {delay:.1f}s.")
            except Exception as e:
                logging.exception(f"Unexpected error while editing channel topic: {e}. Retrying in {delay:.1f}s.")
                raise e
            await asyncio.sleep(delay)
            
    def run(self):
        self.client.run(config.discord.token, log_level=logging.INFO)


class TelegramBotWrapper(BotInterface):
    def __init__(self):
        if not config.telegram.token:
            raise ValueError("TELEGRAM_TOKEN is required when BOT_TYPE is telegram")
        if not config.telegram.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID is required when BOT_TYPE is telegram")
            
        self.bot = TelegramBot(token=config.telegram.token)
        self.chat_id = config.telegram.chat_id
        
    async def initialize(self):
        pass
    
    def setup_error_logging(self):
        pass
                    
    async def send_offers(self, offers: List[RentalOffer]):
        for offer in offers:
            message = self._format_offer_message(offer)
            await self._retry_until_successful_send(message)
            await asyncio.sleep(1.5)  # rate limiting
            
    def _format_offer_message(self, offer: RentalOffer) -> str:
        message = f"*{offer.title}*\n\n"
        message += f"📍 {offer.location}\n"
        message += f"💰 {offer.price} Kč\n"
        message += f"🤖 {offer.scraper.name}\n\n"
        message += f"[Zobrazit nabídku]({offer.link})"
        
        return message

    async def update_status(self, message: str):
        await self._retry_until_successful_send(f"ℹ️ {message}")

    async def _retry_until_successful_send(self, message: str, delay: float = 5.0):
        while True:
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logging.info("Message successfully sent to Telegram.")
                return
            except Exception as e:
                logging.warning(f"Error while sending Telegram message: {e}. Retrying in {delay:.1f}s.")
                await asyncio.sleep(delay)
                
    def run(self):
        pass


def create_bot() -> BotInterface:
    if config.bot_type.lower() == "telegram":
        return TelegramBotWrapper()
    else:
        return DiscordBotWrapper()
