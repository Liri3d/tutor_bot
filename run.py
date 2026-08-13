import os
import asyncio
import uvicorn
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ENVIRONMENT, init_bot_info
from handlers.common import common_router
from handlers.tutor import tutor_router
from services import SessionService
from api.main import app
import subprocess

logging.basicConfig(level=logging.INFO)

RUN_FRONTEND = os.getenv("RUN_FRONTEND", "true").lower() == "true"

def run_sqlite_web():
    """Запуск sqlite-web в фоновом режиме"""
    try:
        db_path = '/data/tutor_bot.db'
        
        # Проверяем базу данных
        if not os.path.exists(db_path):
            print(f"⚠️ База данных не найдена: {db_path}")
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.close()
            print(f"✅ Создана пустая база: {db_path}")
        
        # Запускаем sqlite-web на порту 8080 (внутренний)
        process = subprocess.Popen([
            "sqlite_web",
            "--host", "0.0.0.0",
            "--port", "8080",
            "--read-only",
            db_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"📊 sqlite-web запущен на порту 8080 (внутренний)")
        print(f"🔒 Режим: только для чтения")
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска sqlite-web: {e}")
        return None

async def run_bot():
    """Запуск бота"""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(common_router)
    dp.include_router(tutor_router)
    
    await SessionService.init_db()
    await init_bot_info()
    
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

async def run_api():
    """Запуск FastAPI"""
    env = ENVIRONMENT
    host = "0.0.0.0" if env == "production" else "localhost"
    port = int(os.getenv("PORT", 80))

    config = uvicorn.Config(app, host=host, port=port, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()
    
async def main():
    await SessionService.init_db()

    run_sqlite_web()
    
    await asyncio.gather(run_bot(), run_api()) 

if __name__ == "__main__":
    asyncio.run(main())