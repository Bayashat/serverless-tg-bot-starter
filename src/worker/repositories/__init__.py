import os

TG_USERS_TABLE_NAME = os.environ.get("TG_USERS_TABLE_NAME")
TELEGRAM_API_BASE = os.environ.get("TELEGRAM_API_BASE", "https://api.telegram.org/bot")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not TG_USERS_TABLE_NAME or not BOT_TOKEN:
    raise ValueError("TG_USERS_TABLE_NAME and BOT_TOKEN must be set")
