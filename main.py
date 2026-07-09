import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

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

def get_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data="confirm"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel"
                )
            ]
        ]
    )

class OrderStates(StatesGroup):
    waiting_for_name = State()      # Ждём имя
    waiting_for_address = State()   # Ждём адрес

@dp.message(Command("order"))
async def cmd_order(message: types.Message, state: FSMContext):
    await state.set_state(OrderStates.waiting_for_name)
    await message.answer("Как вас зовут?")

@dp.message(OrderStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderStates.waiting_for_address)
    await message.answer("Введите адрес доставки:")

@dp.message(OrderStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    address = message.text
    
    await message.answer(f"✅ Заказ оформлен!\nИмя: {name}\nАдрес: {address}")
    await state.clear()  # Очищаем состояние


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=get_inline_keyboard()
    )

@dp.callback_query(lambda c: c.data == "confirm")
async def handle_confirm(callback: types.CallbackQuery):
    await callback.answer()  # Убираем "часики" на кнопке
    await callback.message.edit_text("✅ Подтверждено!")

@dp.callback_query(lambda c: c.data == "cancel")
async def handle_cancel(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("❌ Отменено!")

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