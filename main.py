import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import BOT_TOKEN

# Включаем логирование (чтобы видеть ошибки)
logging.basicConfig(level=logging.INFO)

# Создаём бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============================================
# ОБРАБОТЧИКИ СООБЩЕНИЙ
# ============================================

# 1. Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Я бот.")

# 2. Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("📋 Доступные команды: /start, /help")

# 3. Все остальные сообщения
@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")

# ============================================
# ЗАПУСК
# ============================================

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())