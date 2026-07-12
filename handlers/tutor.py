from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

from db import get_session, get_user_by_telegram_id
from keyboards import settings_menu, tutor_main_menu 

tutor_router = Router()

@tutor_router.callback_query(lambda c: c.data == "settings_menu")
async def handle_settings_menu(callback: types.CallbackQuery, state: FSMContext):
    """Открыть меню настроек"""
    await callback.answer()
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден.")
            return
        
        # Показываем меню настроек
        await callback.message.edit_text(
            text=f"⚙️ Настройки\n\n"
                 f"👤 Ваша роль: {user.role}\n"
                 f"📅 Зарегистрирован: {user.registered_at.strftime('%d.%m.%Y')}\n\n"
                 f"Здесь вы можете изменить свои настройки.",
            reply_markup=settings_menu(user.role)
        )


@tutor_router.callback_query(lambda c: c.data == "back_to_main")
async def handle_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться в главное меню из настроек"""
    await callback.answer()
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден.")
            return
        
        # Показываем соответствующее меню
        if user.role == "tutor":
            await callback.message.edit_text(
                text="👋 Главное меню репетитора:",
                reply_markup=tutor_main_menu()
            )