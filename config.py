import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "tutortesting_bot"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if not BOT_TOKEN:
    raise ValueError("Токен не найден!")