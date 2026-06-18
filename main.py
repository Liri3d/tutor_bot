import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ID = int(os.getenv("TUTOR_TELEGRAM_ID", 0))

if not TOKEN:
    raise ValueError("Токен не найден! Проверьте .env файл.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id == ID:
        text = "Здравствуйте, репетитор!"
    else:
        text = "Привет, ученик!"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    user_id = message.from_user.id
    if user_id == ID:
        text = "**Команды репетитора:**\n/add_slot - добавить урок\n/my_slots - мои уроки"
    else:
        text = "**Команды ученика:**\n/slots - свободные уроки\n/book - записаться"
    await message.answer(text, parse_mode="Markdown")



@dp.message(Command("hi"))
async def cmd_help(message: types.Message):
    
    text = "Приветствую))"
    await message.answer(text, parse_mode="Markdown")



@dp.message()
async def unknown(message: types.Message):
    await message.answer("Я не знаю такой команды.")

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())