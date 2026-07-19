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
    await asyncio.gather(run_bot(), run_api())

if __name__ == "__main__":
    asyncio.run(main())