# from aiogram import types, Router
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from datetime import datetime
# from sqlalchemy import select, and_

# from db import get_session
# from db.crud import get_user_by_telegram_id, get_tutor_students
# from db.models import User, Relationship

# # Создаем роутер
# router = Router()


# async def show_tutor_menu(message: types.Message, user: User):
#     """Показать главное меню репетитора"""
#     text = (
#         f"👋 Здравствуйте, {user.first_name or 'репетитор'}!\n\n"
#         "Выберите действие:"
#     )
    
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="📅 Расписание",
#                     callback_data="tutor_schedule"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="👥 Мои ученики",
#                     callback_data="tutor_students"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="➕ Добавить занятие",
#                     callback_data="tutor_add_lesson"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="🔗 Создать приглашение",
#                     callback_data="tutor_invite"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="⚙️ Настройки",
#                     callback_data="tutor_settings"
#                 )
#             ]
#         ]
#     )
    
#     await message.answer(text, reply_markup=keyboard)


# @router.callback_query(lambda c: c.data == "tutor_students")
# async def callback_tutor_students(callback: types.CallbackQuery):
#     """Показать список учеников репетитора"""
#     await callback.answer()
    
#     user_id = callback.from_user.id
    
#     async for session in get_session():
#         user = await get_user_by_telegram_id(session, user_id)
#         if not user:
#             await callback.message.edit_text("❌ Пользователь не найден.")
#             return
        
#         students = await get_tutor_students(session, user.id)
        
#         if not students:
#             text = (
#                 "👥 У вас пока нет учеников.\n\n"
#                 "Создайте приглашение и отправьте его ученикам:\n"
#                 "Нажмите кнопку 'Создать приглашение' в главном меню."
#             )
#             keyboard = InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [
#                         InlineKeyboardButton(
#                             text="🔗 Создать приглашение",
#                             callback_data="tutor_invite"
#                         )
#                     ],
#                     [
#                         InlineKeyboardButton(
#                             text="↩️ Назад в меню",
#                             callback_data="tutor_back"
#                         )
#                     ]
#                 ]
#             )
#             await callback.message.edit_text(text, reply_markup=keyboard)
#             return
        
#         text = "👥 **Ваши ученики:**\n\n"
        
#         keyboard = InlineKeyboardBuilder()
        
#         for student in students:
#             text += f"• {student.first_name or 'Без имени'}"
#             if student.username:
#                 text += f" (@{student.username})"
#             text += "\n"
#             from aiogram import types, Router
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from datetime import datetime
# from sqlalchemy import select, and_

# from db import get_session
# from db.crud import get_user_by_telegram_id, get_tutor_students
# from db.models import User, Relationship

# # Импортируем Reply Keyboard
# from keyboards import get_tutor_keyboard

# router = Router()


# async def show_tutor_menu(message: types.Message, user: User):
#     """Показать главное меню репетитора"""
#     text = (
#         f"👋 Здравствуйте, {user.first_name or 'репетитор'}!\n\n"
#         "Выберите действие с помощью кнопок ниже:"
#     )
    
#     # Используем Reply Keyboard вместо Inline
#     await message.answer(
#         text,
#         reply_markup=get_tutor_keyboard()
#     )


# @router.message(lambda msg: msg.text == "📅 Мои занятия")
# async def handle_my_lessons(message: types.Message):
#     """Обработка кнопки 'Мои занятия' для репетитора"""
#     # ... логика показа занятий


# @router.message(lambda msg: msg.text == "➕ Добавить занятие")
# async def handle_add_lesson(message: types.Message):
#     """Обработка кнопки 'Добавить занятие'"""
#     # ... логика добавления занятия


# @router.message(lambda msg: msg.text == "👥 Мои ученики")
# async def handle_my_students(message: types.Message):
#     """Обработка кнопки 'Мои ученики'"""
#     # ... логика показа учеников


# @router.message(lambda msg: msg.text == "🔗 Пригласить ученика")
# async def handle_invite(message: types.Message):
#     """Обработка кнопки 'Пригласить ученика'"""
#     # ... логика создания инвайта


# @router.message(lambda msg: msg.text == "⚙️ Настройки")
# async def handle_settings(message: types.Message):
#     """Обработка кнопки 'Настройки'"""
#     # ... логика настроек
#             # Добавляем кнопку для управления учеником
#             keyboard.button(
#                 text=f"📋 {student.first_name or 'Ученик'}",
#                 callback_data=f"student_manage_{student.id}"
#             )
        
#         keyboard.button(
#             text="🔗 Создать приглашение",
#             callback_data="tutor_invite"
#         )
#         keyboard.button(
#             text="↩️ Назад в меню",
#             callback_data="tutor_back"
#         )
#         keyboard.adjust(1, 1)
        
#         await callback.message.edit_text(
#             text,
#             parse_mode="Markdown",
#             reply_markup=keyboard.as_markup()
#         )


# @router.callback_query(lambda c: c.data == "tutor_invite")
# async def callback_tutor_invite(callback: types.CallbackQuery):
#     """Создать приглашение для ученика"""
#     await callback.answer()
    
#     user_id = callback.from_user.id
    
#     async for session in get_session():
#         user = await get_user_by_telegram_id(session, user_id)
#         if not user or user.role != 'tutor':
#             await callback.message.edit_text("❌ Только репетитор может создавать приглашения.")
#             return
        
#         from datetime import datetime, timedelta
#         from db.crud import create_invite
#         from config import config
        
#         # Создаём приглашение на 7 дней
#         expires_at = datetime.now() + timedelta(days=config.INVITE_EXPIRE_DAYS)
#         invite = await create_invite(session, user.id, expires_at)
#         await session.commit()
        
#         bot_username = (await callback.bot.get_me()).username
        
#         text = (
#             "🔗 **Ваша ссылка-приглашение создана!**\n\n"
#             f"Отправьте её ученику:\n"
#             f"`https://t.me/{bot_username}?start=invite_{invite.code}`\n\n"
#             f"Код приглашения: `{invite.code}`\n"
#             f"Действительно до: {expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
#             "ℹ️ Ученик может использовать ссылку или ввести код вручную."
#         )
        
#         keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [
#                     InlineKeyboardButton(
#                         text="📋 Скопировать ссылку",
#                         callback_data=f"copy_{invite.code}"
#                     )
#                 ],
#                 [
#                     InlineKeyboardButton(
#                         text="↩️ Назад в меню",
#                         callback_data="tutor_back"
#                     )
#                 ]
#             ]
#         )
        
#         await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


# @router.callback_query(lambda c: c.data == "tutor_back")
# async def callback_tutor_back(callback: types.CallbackQuery):
#     """Вернуться в главное меню репетитора"""
#     await callback.answer()
    
#     user_id = callback.from_user.id
    
#     async for session in get_session():
#         user = await get_user_by_telegram_id(session, user_id)
#         if user:
#             await show_tutor_menu(callback.message, user)
#         else:
#             await callback.message.edit_text("❌ Пользователь не найден.")


# @router.callback_query(lambda c: c.data.startswith("student_manage_"))
# async def callback_student_manage(callback: types.CallbackQuery):
#     """Управление конкретным учеником"""
#     await callback.answer()
    
#     student_id = int(callback.data.split("_")[2])
#     user_id = callback.from_user.id
    
#     async for session in get_session():
#         # Получаем ученика
#         student = await session.get(User, student_id)
#         if not student:
#             await callback.message.edit_text("❌ Ученик не найден.")
#             return
        
#         text = (
#             f"📋 **Управление учеником**\n\n"
#             f"👤 {student.first_name or 'Без имени'}"
#             f"{' (@' + student.username + ')' if student.username else ''}\n\n"
#             "Выберите действие:"
#         )
        
#         keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [
#                     InlineKeyboardButton(
#                         text="📅 Занятия ученика",
#                         callback_data=f"student_lessons_{student_id}"
#                     )
#                 ],
#                 [
#                     InlineKeyboardButton(
#                         text="💰 Баланс занятий",
#                         callback_data=f"student_balance_{student_id}"
#                     )
#                 ],
#                 [
#                     InlineKeyboardButton(
#                         text="⏸️ Приостановить",
#                         callback_data=f"student_pause_{student_id}"
#                     )
#                 ],
#                 [
#                     InlineKeyboardButton(
#                         text="🔴 Отвязать ученика",
#                         callback_data=f"student_remove_{student_id}"
#                     )
#                 ],
#                 [
#                     InlineKeyboardButton(
#                         text="↩️ Назад к ученикам",
#                         callback_data="tutor_students"
#                     )
#                 ]
#             ]
#         )
        
#         await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


# @router.callback_query(lambda c: c.data.startswith("student_remove_"))
# async def callback_student_remove(callback: types.CallbackQuery):
#     """Отвязать ученика"""
#     await callback.answer()
    
#     student_id = int(callback.data.split("_")[2])
#     user_id = callback.from_user.id
    
#     async for session in get_session():
#         user = await get_user_by_telegram_id(session, user_id)
#         if not user:
#             await callback.message.edit_text("❌ Пользователь не найден.")
#             return
        
#         # Находим связь
#         stmt = select(Relationship).where(
#             and_(
#                 Relationship.tutor_id == user.id,
#                 Relationship.student_id == student_id,
#                 Relationship.status == 'active'
#             )
#         )
#         result = await session.execute(stmt)
#         relationship = result.scalar_one_or_none()
        
#         if not relationship:
#             await callback.message.edit_text("❌ Связь с учеником не найдена.")
#             return
        
#         text = (
#             "⚠️ **Подтверждение отвязки**\n\n"
#             "Вы уверены, что хотите отвязать ученика?\n\n"
#             "❌ Все будущие занятия будут отменены.\n"
#             "❌ Связь будет разорвана.\n\n"
#             "Ученик получит уведомление."
#         )
        
#         keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [
#                     InlineKeyboardButton(
#                         text="✅ Да, отвязать",
#                         callback_data=f"student_remove_confirm_{student_id}"
#                     )
#                 ],
#                 [
#                     InlineKeyboardButton(
#                         text="❌ Нет, отмена",
#                         callback_data=f"student_manage_{student_id}"
#                     )
#                 ]
#             ]
#         )
        
#         await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


# @router.callback_query(lambda c: c.data.startswith("student_remove_confirm_"))
# async def callback_student_remove_confirm(callback: types.CallbackQuery):
#     """Подтверждение отвязки ученика"""
#     await callback.answer()
    
#     student_id = int(callback.data.split("_")[3])
#     user_id = callback.from_user.id
    
#     async for session in get_session():
#         try:
#             user = await get_user_by_telegram_id(session, user_id)
#             if not user:
#                 await callback.message.edit_text("❌ Пользователь не найден.")
#                 return
            
#             # Находим связь
#             stmt = select(Relationship).where(
#                 and_(
#                     Relationship.tutor_id == user.id,
#                     Relationship.student_id == student_id
#                 )
#             )
#             result = await session.execute(stmt)
#             relationship = result.scalar_one_or_none()
            
#             if not relationship:
#                 await callback.message.edit_text("❌ Связь не найдена.")
#                 return
            
#             # Отвязываем ученика
#             relationship.status = 'inactive'
#             relationship.updated_at = datetime.now()
            
#             # Отменяем все будущие занятия
#             from db.models import Lesson
#             stmt = select(Lesson).where(
#                 and_(
#                     Lesson.relationship_id == relationship.id,
#                     Lesson.status == 'scheduled',
#                     Lesson.start_time > datetime.now()
#                 )
#             )
#             result = await session.execute(stmt)
#             lessons = result.scalars().all()
            
#             for lesson in lessons:
#                 lesson.status = 'cancelled'
            
#             await session.commit()
            
#             # Получаем информацию об ученике
#             student = await session.get(User, student_id)
            
#             # Уведомляем ученика
#             try:
#                 await callback.bot.send_message(
#                     student.telegram_id,
#                     "⚠️ Репетитор отвязал вас.\n\n"
#                     "Все будущие занятия были отменены.\n"
#                     "Если это ошибка, свяжитесь с репетитором."
#                 )
#             except Exception as e:
#                 logging.error(f"Не удалось уведомить ученика: {e}")
            
#             await callback.message.edit_text(
#                 "✅ Ученик успешно отвязан.\n"
#                 "Все будущие занятия отменены."
#             )
            
#             # Через 2 секунды возвращаемся к списку учеников
#             await asyncio.sleep(2)
#             await callback_tutor_students(callback)
            
#         except Exception as e:
#             await session.rollback()
#             logging.error(f"Ошибка при отвязке ученика: {e}")
#             await callback.message.edit_text("❌ Произошла ошибка при отвязке ученика.")




from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from sqlalchemy import select, and_

from db import get_session
from db.crud import get_user_by_telegram_id, get_tutor_students
from db.models import User, Relationship

# Импортируем Reply Keyboard
from keyboards import get_tutor_keyboard

router = Router()


async def show_tutor_menu(message: types.Message, user: User):
    """Показать главное меню репетитора"""
    text = (
        f"👋 Здравствуйте, {user.first_name or 'репетитор'}!\n\n"
        "Выберите действие с помощью кнопок ниже:"
    )
    
    # Используем Reply Keyboard вместо Inline
    await message.answer(
        text,
        reply_markup=get_tutor_keyboard()
    )


@router.message(lambda msg: msg.text == "📅 Мои занятия")
async def handle_my_lessons(message: types.Message):
    """Обработка кнопки 'Мои занятия' для репетитора"""
    # ... логика показа занятий


@router.message(lambda msg: msg.text == "➕ Добавить занятие")
async def handle_add_lesson(message: types.Message):
    """Обработка кнопки 'Добавить занятие'"""
    # ... логика добавления занятия


@router.message(lambda msg: msg.text == "👥 Мои ученики")
async def handle_my_students(message: types.Message):
    """Обработка кнопки 'Мои ученики'"""
    # ... логика показа учеников


@router.message(lambda msg: msg.text == "🔗 Пригласить ученика")
async def handle_invite(message: types.Message):
    """Обработка кнопки 'Пригласить ученика'"""
    # ... логика создания инвайта


@router.message(lambda msg: msg.text == "⚙️ Настройки")
async def handle_settings(message: types.Message):
    """Обработка кнопки 'Настройки'"""
    # ... логика настроек