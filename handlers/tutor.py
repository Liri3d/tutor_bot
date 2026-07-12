from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

from db import (
    get_session,
    get_user_by_id,
    get_user_by_telegram_id,
    get_active_relationships_for_tutor,
)
    
from keyboards import (
    settings_menu,
    tutor_main_menu,
    build_students_keyboard,
    student_detail_menu
)

from states import TutorStates
from services import InviteService, RelationshipService, UserService

tutor_router = Router()

@tutor_router.callback_query(lambda c: c.data == "tutor_students")
async def handle_tutor_students(callback: types.CallbackQuery, state: FSMContext):
    """Репетитор хочет просмотреть список учеников"""
    await callback.answer()
    
    # Проверяем, что пользователь — репетитор
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user or user.role != "tutor":
            await callback.message.edit_text("❌ Только репетитор может просмотреть список учеников.")
            return
    
        # Получаем учеников через сервис
        students = await RelationshipService.get_tutor_students(session, user.id)

        if students:
            response_text = f"👤 **Ваши ученики**\n\nВсего: {len(students)}"
            keyboard = build_students_keyboard(students, user.id)
            await callback.message.edit_text(
                text=response_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                text="👤 У вас пока нет учеников.\n\nСоздайте приглашение, чтобы добавить ученика.",
                reply_markup=tutor_main_menu()
            )
    
@tutor_router.callback_query(lambda c: c.data and c.data.startswith("student_"))
async def handle_student_click(callback: types.CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку ученика"""
    await callback.answer()
    
    # Извлекаем ID ученика из callback_data
    student_id = int(callback.data.split("_")[1])
    
    async for session in get_session():
        # Получаем ученика через сервис
        student = await UserService.get_user_by_id(session, student_id)
        
        if not student:
            await callback.message.edit_text("❌ Ученик не найден.")
            return
        
        # Показываем информацию об ученике (заглушка)
        await callback.message.edit_text(
            f"📋 **Информация об ученике**\n\n"
            f"👤 Имя: {student.first_name or 'Не указано'}\n"
            f"🔗 Username: @{student.username if student.username else 'Нет'}\n"
            f"📅 Зарегистрирован: {student.registered_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Здесь будут занятия и управление учеником.",
            parse_mode="Markdown",
            reply_markup=student_detail_menu(student_id)
        )

@tutor_router.callback_query(lambda c: c.data == "tutor_invite")
async def handle_tutor_invite(callback: types.CallbackQuery, state: FSMContext):
    """Репетитор хочет пригласить ученика"""
    await callback.answer()
    
    # Проверяем, что пользователь — репетитор
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user or user.role != "tutor":
            await callback.message.edit_text("❌ Только репетитор может приглашать учеников.")
            return
    
    await callback.message.edit_text(
        "👤 Пригласить ученика\n\n"
        "Введите имя ученика, которого хотите пригласить:"
    )
    await state.set_state(TutorStates.waiting_for_student_name)

@tutor_router.message(TutorStates.waiting_for_student_name)
async def handle_student_name_input(message: types.Message, state: FSMContext):
    """Репетитор ввел имя ученика"""
    student_name = message.text.strip()
    
    if len(student_name) < 2:
        await message.answer(
            "❌ Имя должно содержать хотя бы 2 символа. Попробуйте снова:"
        )
        return
    
    async for session in get_session():
        # Получаем репетитора
        tutor = await get_user_by_telegram_id(session, message.from_user.id)
        if not tutor:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return
        
        invite = await InviteService.create_invite(
            session=session,
            tutor_id=tutor.id,
            student_name=student_name,
            expires_in_days=1  # 24 часа
        )
        
        # Формируем сообщение
        bot_username = (await message.bot.get_me()).username
        
        await message.answer(
            f"✅ Приглашение создано!\n\n"
            f"👤 Ученик: {student_name}\n"
            f"🔑 Код: `{invite.code}`\n"
            f"📅 Действительно до: {invite.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Отправьте ученику эту ссылку:\n"
            f"`https://t.me/{bot_username}?start=invite_{invite.code}`\n\n"
            f"ℹ️ Ссылка действительна 24 часа.\n"
            f"ℹ️ После использования ссылка становится недействительной.",
            parse_mode="Markdown"
        )
        
        await state.clear()
        
        # Возвращаемся в меню
        await message.answer(
            "Меню репетитора:",
            reply_markup=tutor_main_menu()
        )

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

@tutor_router.callback_query(lambda c: c.data == "back_to_tutor_students")
async def handle_back_to_tutor_students(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к просмотру списка учеников"""
    await callback.answer()
    
    # Просто вызываем обработчик списка учеников
    await handle_tutor_students(callback, state)