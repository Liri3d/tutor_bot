from aiogram import types, Router
from aiogram.fsm.context import FSMContext

# from db import *
    
from keyboards import (
    settings_menu,
    tutor_main_menu,
    build_students_keyboard,
    student_detail_menu
)

from states import TutorStates
from services import *

tutor_router = Router()

async def _show_students_list(
    callback: types.CallbackQuery,
    session,
    user
) -> None:
    """
    Общая логика показа списка учеников.
    Используется в handle_tutor_students и handle_back_to_tutor_students.
    """
    students = await RelationshipService.get_tutor_students(session, user.id)

    if students:
        response_text = await MessageService.format_student_list(students)
        keyboard = build_students_keyboard(students, user.id)
        
        await callback.message.edit_text(
            text=response_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            text=await MessageService.get_error_message("no_students"),
            reply_markup=tutor_main_menu()
        )

@tutor_router.callback_query(lambda c: c.data == "tutor_students")
async def handle_tutor_students(callback: types.CallbackQuery, state: FSMContext):
    """Репетитор хочет просмотреть список учеников"""
    await callback.answer()
    
    # Проверяем, что пользователь — репетитор
    async for session in SessionService.get_session():
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        if not user or user.role != "tutor":
            await callback.message.edit_text(await MessageService.get_error_message("permission_denied"))
            return

        await _show_students_list(callback, session, user)

@tutor_router.callback_query(lambda c: c.data and c.data.startswith("student_"))
async def handle_student_click(callback: types.CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку ученика"""
    await callback.answer()
    
    # Извлекаем ID ученика из callback_data
    student_id = int(callback.data.split("_")[1])
    
    async for session in SessionService.get_session():
        if not await UserService.is_tutor(session, callback.from_user.id):
            await callback.message.edit_text(
                await MessageService.get_error_message("permission_denied")
            )
            return
        
        # Получаем ученика через сервис   
        student = await UserService.get_user_by_id(session, student_id)
        if not student:
            await callback.message.edit_text(await MessageService.get_error_message("student_not_found"))
            return
        
        student_info = await MessageService.format_student_detail(student)

        # Показываем информацию об ученике (заглушка)
        await callback.message.edit_text(
            text = student_info,
            parse_mode="Markdown",
            reply_markup=student_detail_menu(student_id)
        )

@tutor_router.callback_query(lambda c: c.data == "tutor_invite")
async def handle_tutor_invite(callback: types.CallbackQuery, state: FSMContext):
    """Репетитор хочет пригласить ученика"""
    await callback.answer()
    
    # Проверяем, что пользователь — репетитор
    async for session in SessionService.get_session():
        if not await UserService.is_tutor(session, callback.from_user.id):
            await MessageService.get_error_message("permission_denied")
            return
    
    await callback.message.edit_text(
        await MessageService.get_invite_prompt()
    )
    await state.set_state(TutorStates.waiting_for_student_name)

@tutor_router.message(TutorStates.waiting_for_student_name)
async def handle_student_name_input(message: types.Message, state: FSMContext):
    """Репетитор ввел имя ученика"""
    student_name = message.text.strip()
    
    if len(student_name) < 2:
        await message.answer(
            await MessageService.get_error_message("invalid_name")
        )
        return
    
    async for session in SessionService.get_session():
        # Получаем репетитора
        tutor = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        if not tutor:
            await message.answer(await MessageService.get_error_message("user_not_found"))
            await state.clear()
            return
        
        invite = await InviteService.create_invite(
            session=session,
            tutor_id=tutor.id,
            student_name=student_name,
            expires_in_days=1  
        )
        
        # Формируем сообщение
        bot_username = (await message.bot.get_me()).username
        await message.answer(
            await MessageService.format_invite(invite, bot_username),
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
    
    async for session in SessionService.get_session():
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.edit_text(await MessageService.get_error_message("user_not_found"))
            return
        
        settings_text = await MessageService.get_settings_message(user)

        # Показываем меню настроек
        await callback.message.edit_text(
            text=settings_text,
            reply_markup=settings_menu(user.role),
            parse_mode="Markdown"
        )

@tutor_router.callback_query(lambda c: c.data == "back_to_tutor_students")
async def handle_back_to_tutor_students(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к просмотру списка учеников"""
    await callback.answer()
    
    async for session in SessionService.get_session():
        if not await UserService.is_tutor(session, callback.from_user.id):
            await callback.message.edit_text(
                await MessageService.get_error_message("permission_denied")
            )
            return
        
        user = await UserService.get_user_by_telegram_id(
            session, callback.from_user.id
        )
        await _show_students_list(callback, session, user)