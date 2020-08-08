import os

from dotenv import load_dotenv

load_dotenv('.env')

CHANNEL_CHAT_ID = os.getenv("CHANNEL_CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
VOICE_DURATION_LIMIT = os.getenv("VOICE_DURATION_LIMIT")
