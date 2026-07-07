import logging

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import get_session
from db.crud import get_user_by_telegram_id

from .registration import register_student_by_invite, register_tutor
from .tutor import show_tutor_menu
from .student import show_student_menu

logger = logging.getLogger(__name__)


async def cmd_start(message: types.Message):
    """Обработка команды /start"""
    user_id = message.from_user.id
    args = message.text.split()
    invite_code = None
    
    if len(args) > 1:
        param = args[1]
        if param.startswith("invite_"):
            invite_code = param[7:]
        else:
            invite_code = param
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, user_id)
        
        if user:
            # Уже зарегистрирован
            if user.role == "tutor":
                await show_tutor_menu(message, user)
            else:
                await show_student_menu(message, user)
            return
        
        if invite_code:
            # Регистрация по приглашению
            await handle_invite_registration(message, session, invite_code)
        else:
            # Предлагаем выбрать роль
            await ask_role(message)


async def ask_role(message: types.Message):
    """Запросить роль у пользователя"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍🏫 Я репетитор", callback_data="role_tutor")],
            [InlineKeyboardButton(text="👨‍🎓 Я ученик", callback_data="role_student")]
        ]
    )
    await message.answer(
        "👋 Добро пожаловать в Tutor Bot!\n\nВыберите вашу роль:",
        reply_markup=keyboard
    )


async def handle_role_tutor(callback: types.CallbackQuery):
    """Обработка выбора роли репетитор"""
    await callback.answer()
    user_id = callback.from_user.id

    async for session in get_session():
        user = await get_user_by_telegram_id(session, user_id)
        if user:
            if user.role == 'tutor':
                await show_tutor_menu(callback.message, user)
            else:
                await callback.message.answer("❌ Вы уже зарегистрированы как ученик.")
            return

        try:
            tutor = await register_tutor(
                session=session,
                telegram_id=user_id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
            )
            await session.commit()
            await show_tutor_menu(callback.message, tutor)
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            await callback.message.answer("❌ Ошибка при регистрации репетитора.")


async def handle_role_student(callback: types.CallbackQuery):
    """Обработка выбора роли ученик (без инвайта)"""
    await callback.answer()
    user_id = callback.from_user.id

    async for session in get_session():
        user = await get_user_by_telegram_id(session, user_id)
        if user:
            if user.role == 'student':
                await show_student_menu(callback.message, user)
                return
            await callback.message.answer("❌ Вы уже зарегистрированы как репетитор.")
            return

        await callback.message.answer(
            "👨‍🎓 Ученики подключаются к репетитору по приглашению.\n\n"
            "Получите инвайт-ссылку от репетитора и откройте её — тогда вы сможете зарегистрироваться."
        )


async def handle_invite_registration(message: types.Message, session, invite_code: str):
    """Обработка регистрации по приглашению"""
    user_id = message.from_user.id
    
    try:
        tutor, relationship = await register_student_by_invite(
            session=session,
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            invite_code=invite_code
        )
        
        await session.commit()
        
        await message.answer(
            "✅ Вы успешно подключились к репетитору!\n\n"
            "Используйте /help для списка команд."
        )
        
        # Уведомляем репетитора
        try:
            await message.bot.send_message(
                tutor.telegram_id,
                f"🎉 К вам подключился новый ученик!\n\n"
                f"👤 {message.from_user.first_name or 'Без имени'}"
                f"{' (@' + message.from_user.username + ')' if message.from_user.username else ''}"
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить репетитора: {e}")
        
    except ValueError as e:
        await message.answer(f"❌ {str(e)}")
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при регистрации: {e}")
        await message.answer("❌ Произошла ошибка при регистрации.")