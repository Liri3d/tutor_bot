# handlers/common.py
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
import logging

from states import RegisterStates
from keyboards import (
    role_keyboard,
    student_main_menu,
    tutor_main_menu,
    settings_menu,
    confirm_change_role_menu
)
from services import (
    SessionService,
    StudentService,
    NotificationService,
    MessageService,
    AuthService,
    InviteService,
)
from db import student_crud, tutor_crud

common_router = Router()


@common_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    args = message.text.split()
    invite_code = None
    
    if len(args) > 1:
        param = args[1]
        if param.startswith("invite_"):
            invite_code = param[7:]  
        else:
            invite_code = param 

    await message.answer(
        text="Загрузка...",
        reply_markup=ReplyKeyboardRemove()
    )

    async for session in SessionService.get_session():
        # Проверяем, есть ли пользователь в БД
        student = await student_crud.get_by_telegram_id(session, message.from_user.id)
        tutor = None
        
        # Если не нашли ученика, может быть репетитор (у них нет telegram_id)
        # В текущей архитектуре репетиторы не имеют telegram_id, поэтому ищем по-другому
        # Для MVP: если есть инвайт-код — регистрируем ученика
        # Если нет — предлагаем выбрать роль

        if invite_code:
            try:
                # Регистрируем ученика по инвайту
                student, tutor = await StudentService.register_by_invite(
                    session=session,
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    invite_code=invite_code
                )

                success_text = await MessageService.get_registration_success_message(
                    student, "student"
                )
                await message.answer(success_text, parse_mode="Markdown")
                
                await NotificationService.notify_tutor_about_new_student(
                    bot=message.bot,
                    tutor_telegram_id=tutor.telegram_id,
                    student_first_name=student.first_name or "Без имени",
                    student_username=student.username
                )
                
                await message.answer(
                    "Выберите действие:",
                    reply_markup=student_main_menu()
                )
                
                await state.clear()
                return

            except ValueError as e:
                await message.answer(f"❌ {str(e)}")
                return
                   
        # Если пользователь уже зарегистрирован как ученик
        if student:
            welcome_text, welcome_keyboard = await MessageService.get_welcome_message(student)
            await message.answer(welcome_text, reply_markup=welcome_keyboard)
            return
            
        # Для репетиторов: нужно искать по другому признаку
        # В текущей архитектуре у репетитора нет telegram_id,
        # поэтому проверяем, не зарегистрирован ли уже пользователь как репетитор
        # (для MVP можно сделать через дополнительный запрос)
        
        # Если пользователь не зарегистрирован и нет кода — предлагаем выбрать роль
        await state.set_state(RegisterStates.waiting_for_role)
        await message.answer(
            await MessageService.get_start_message(),
            reply_markup=role_keyboard()
        )


@common_router.callback_query(lambda c: c.data == "role_tutor")
async def handle_role_tutor(callback: types.CallbackQuery, state: FSMContext):
    """Пользователь выбрал роль репетитора"""
    await callback.answer() 
    
    async for session in SessionService.get_session():
        # Проверяем, не зарегистрирован ли уже пользователь
        existing = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if existing:
            await callback.message.edit_text(
                "✅ Вы уже зарегистрированы как репетитор!"
            )
            await callback.message.answer(
                "Выберите действие:",
                reply_markup=tutor_main_menu()
            )
            await state.clear()
            return
        
        # Создаём репетитора из данных Telegram
        tutor = await tutor_crud.create(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name or "Репетитор"
        )

    await callback.message.edit_text(
        f"✅ **Регистрация успешна!**\n\n"
        f"👤 Вы зарегистрированы как репетитор:\n"
        f"Имя: {tutor.first_name}\n"
        f"{'Username: @' + tutor.username if tutor.first_name else ''}\n"
        f"🆔 Telegram ID: {tutor.telegram_id}\n\n"
        f"Теперь вы можете управлять своими учениками через бота!",
        parse_mode="Markdown"
    )
    
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=tutor_main_menu()
    )
    await state.clear()


@common_router.callback_query(lambda c: c.data == "role_student")
async def handle_role_student(callback: types.CallbackQuery, state: FSMContext):
    """Пользователь выбрал роль ученика"""
    await callback.answer()
    
    async for session in SessionService.get_session():
        # Проверяем, не зарегистрирован ли уже
        existing = await student_crud.get_by_telegram_id(session, callback.from_user.id)
        if existing:
            await callback.message.edit_text(
                "✅ Вы уже зарегистрированы как ученик!"
            )
            await state.clear()
            return
        
        # Создаём ученика
        student = await student_crud.create(
            session=session,
            telegram_id=callback.from_user.id,
            first_name=callback.from_user.first_name or "Ученик",
            username=callback.from_user.username
        )

    success_text = await MessageService.get_registration_success_message(student, "student")
    instructions = await MessageService.get_invite_instructions()
    
    await callback.message.edit_text(
        f"{success_text}{instructions}",
        parse_mode="Markdown"
    )
    await state.set_state(RegisterStates.waiting_for_invite)


# @common_router.message(RegisterStates.waiting_for_invite)
# async def handle_invite_input(message: types.Message, state: FSMContext):
#     """Ученик переходит по ссылке-приглашению"""
#     invite_code = message.text.strip()

#     async for session in SessionService.get_session():
#         try:
#             student, tutor = await StudentService.register_by_invite(
#                 session=session,
#                 telegram_id=message.from_user.id,
#                 username=message.from_user.username,
#                 first_name=message.from_user.first_name,
#                 invite_code=invite_code
#             )
        
#             success_text = await MessageService.get_connect_success_message(tutor)
        
#             await message.answer(
#                 success_text,
#                 parse_mode="Markdown"
#             )

#             await NotificationService.notify_tutor_about_new_student(
#                 bot=message.bot,
#                 tutor_telegram_id=tutor.telegram_id,
#                 student_first_name=student.first_name or "Без имени",
#                 student_username=student.username
#             )

#             await message.answer(
#                 "Выберите действие:",
#                 reply_markup=student_main_menu()
#             )
        
#             await state.clear()

#         except ValueError as e:
#             await message.answer(f"❌ {str(e)}")


@common_router.callback_query(lambda c: c.data == "back_to_main")
async def handle_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    await callback.answer()
    
    async for session in SessionService.get_session():
        tutor = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if tutor:
            # Если репетитор - показываем меню репетитора
            await callback.message.edit_text(
                "👋 Главное меню репетитора:\n\n"
                "Выберите действие:",
                reply_markup=tutor_main_menu()
            )
            await state.clear()
            return
        
        student = await student_crud.get_by_telegram_id(session, callback.from_user.id)
        if student:
            # Если ученик - показываем меню ученика
            await callback.message.edit_text(
                "👋 Главное меню ученика:\n\n"
                "Выберите действие:",
                reply_markup=student_main_menu()
            )
            await state.clear()
            return
        
        # Если пользователь не найден
        await callback.message.edit_text(
            "❌ Пользователь не найден.\n"
            "Нажмите /start для регистрации."
        )


# @common_router.callback_query(lambda c: c.data == "settings_menu")
# async def handle_settings_menu(callback: types.CallbackQuery, state: FSMContext):
#     """Открыть меню настроек"""
#     await callback.answer()
    
#     async for session in SessionService.get_session():
#         student = await student_crud.get_by_telegram_id(session, callback.from_user.id)
        
#         if not student:
#             await callback.message.edit_text(
#                 await MessageService.get_error_message("user_not_found")
#             )
#             return
        
#         settings_text = await MessageService.get_settings_message(student)
        
#         await callback.message.edit_text(
#             text=settings_text,
#             reply_markup=settings_menu("student"),  # только ученик
#             parse_mode="Markdown"
#         )


# # ===== УДАЛЯЕМ ВСЁ, ЧТО СВЯЗАНО С USER =====
# # - handle_change_role_confirm (нет смены роли)
# # - handle_change_role_yes (нет смены роли)
# # - handle_change_role_no (нет смены роли)
# # - change_role_confirm, change_role_yes, change_role_no callback'и

# # Вместо этого можно добавить простой выход из аккаунта
# @common_router.callback_query(lambda c: c.data == "logout")
# async def handle_logout(callback: types.CallbackQuery, state: FSMContext):
#     """Выйти из аккаунта"""
#     await callback.answer()
#     await state.clear()
#     await callback.message.edit_text(
#         "👋 Вы вышли из аккаунта.\n\n"
#         "Нажмите /start для повторной регистрации."
#     )