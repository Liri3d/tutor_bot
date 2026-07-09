import logging

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from services import get_user_by_telegram, get_or_create_user, get_session
from services.relationship_service import register_student_by_invite as service_register_student

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
        # Используем СЕРВИС вместо CRUD
        user = await get_user_by_telegram(session, user_id)
        
        if user:
            if user.role == "tutor":
                await show_tutor_menu(message, user)
            else:
                await show_student_menu(message, user)
            return
        
        if invite_code:
            await handle_invite_registration(message, session, invite_code)
        else:
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
        user = await get_user_by_telegram(session, user_id)
        if user:
            if user.role == 'tutor':
                await show_tutor_menu(callback.message, user)
            else:
                await callback.message.answer("❌ Вы уже зарегистрированы как ученик.")
            return

        try:
            # Используем СЕРВИС
            tutor = await get_or_create_user(
                session=session,
                telegram_id=user_id,
                role='tutor',
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
        user = await get_user_by_telegram(session, user_id)
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
        tutor, relationship = await service_register_student(
            session=session,
            telegram_id=user_id,
            invite_code=invite_code,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
        
        await session.commit()
        
        # Получаем ученика для меню
        student = await get_user_by_telegram(session, user_id)
        await show_student_menu(message, student)
        
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