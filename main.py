import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ID = int(os.getenv("TUTOR_TELEGRAM_ID", 0))

if not TOKEN:
    raise ValueError("Токен не найден! Проверьте .env файл.")