import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN

# Включаем логирование (чтобы видеть ошибки)
logging.basicConfig(level=logging.INFO)

# Создаём бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="👤 Профиль")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True  # Чтобы кнопки были удобного размера
    )





@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda msg: msg.text == "📅 Расписание")
async def handle_schedule(message: types.Message):
    await message.answer("📅 Ваше расписание: ...")

@dp.message(lambda msg: msg.text == "👤 Профиль")
async def handle_profile(message: types.Message):
    await message.answer("👤 Ваш профиль: ...")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("📋 Доступные команды: /start, /help")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())