# run.py

import asyncio
import uvicorn
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.common import common_router
from handlers.tutor import tutor_router
from services import SessionService
from api.main import app

logging.basicConfig(level=logging.INFO)

async def run_bot():
    """Запуск бота"""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(common_router)
    dp.include_router(tutor_router)
    
    await SessionService.init_db()
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

async def run_api():
    """Запуск FastAPI"""
    config = uvicorn.Config(app, host="localhost", port=8000, loop="asyncio") # 0.0.0.0
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await SessionService.init_db()
    await asyncio.gather(run_bot(), run_api())

if __name__ == "__main__":
    asyncio.run(main())