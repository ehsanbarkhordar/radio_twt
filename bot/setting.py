import os

from dotenv import load_dotenv

load_dotenv('.env')

CHANNEL_CHAT_ID = os.getenv("CHANNEL_CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
