import os
from dotenv import load_dotenv


app_env = os.getenv("APP_ENV")
if app_env:
    load_dotenv(".env." + app_env)

load_dotenv(".env")


FOUND_OFFERS_FILE = os.getenv("FOUND_OFFERS_FILE")

REFRESH_INTERVAL_MINUTES = int(os.getenv("REFRESH_INTERVAL_MINUTES"))

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

DISCORD_OFFERS_CHANNEL = int(os.getenv('DISCORD_OFFERS_CHANNEL'))

DISCORD_DEV_CHANNEL = int(os.getenv('DISCORD_DEV_CHANNEL'))
