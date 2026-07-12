import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.common import common_router
from handlers.tutor import tutor_router
from db.session import init_db

# Включаем логирование (чтобы видеть ошибки)
logging.basicConfig(level=logging.INFO)

# Создаём бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(common_router)
dp.include_router(tutor_router)



async def main():
    await init_db()

    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())