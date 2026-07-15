from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
import logging

from states import RegisterStates
from keyboards import role_keyboard

from keyboards import *

from services import *

common_router = Router()

@common_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    # Парсим параметры команды 
    args = message.text.split()
    invite_code = None
    
    if len(args) > 1:
        param = args[1]
        # Проверяем, начинается ли параметр с invite_
        if param.startswith("invite_"):
            invite_code = param[7:]  
        else:
            invite_code = param 

    await message.answer(
        text="Загрузка...",
        reply_markup=ReplyKeyboardRemove()
    )

    async for session in SessionService.get_session():
        user = await UserService.get_user_by_telegram_id(
            session, message.from_user.id
        ) 

        if invite_code:
            try:
                student, relationship, tutor = await StudentService.register_by_invite(
                    session=session,
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    invite_code=invite_code
                )

                # Уведомляем ученика
                success_text = await MessageService.get_registration_success_message(
                    student, "student"
                )
                await message.answer(success_text, parse_mode="Markdown")
                
                # Уведомляем репетитора
                await NotificationService.notify_tutor_about_new_student(
                    bot=message.bot,
                    tutor_telegram_id=tutor.telegram_id,
                    student_first_name=student.first_name or "Без имени",
                    student_username=student.username
                )
                
                # Показываем меню ученика
                await message.answer(
                    "Выберите действие:",
                    reply_markup=student_main_menu()
                )
                
                await state.clear()
                return

            except ValueError as e:
                await message.answer(f"❌ {str(e)}")
                return
                   
        # Если пользователь уже зарегистрирован
        if user:
            welcome_text, welcome_keyboard = await MessageService.get_welcome_message(user)
            await message.answer(welcome_text, reply_markup=welcome_keyboard)
            
            return
            
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
    
    # Сохраняем пользователя в БД
    async for session in SessionService.get_session():
        user = await UserService.create_user(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            role="tutor"
        )

    success_text = await MessageService.get_registration_success_message(user, "tutor")
        
    await callback.message.edit_text(success_text, parse_mode="Markdown")
    await callback.message.answer(
        "Меню репетитора:",
        reply_markup=tutor_main_menu()
    )

@common_router.callback_query(lambda c: c.data == "role_student")
async def handle_role_student(callback: types.CallbackQuery, state: FSMContext):
    """Пользователь выбрал роль ученика"""
    await callback.answer()
    
    async for session in SessionService.get_session():
        user = await UserService.create_user(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            role="student"
        )

    success_text = await MessageService.get_registration_success_message(user, "student")
    instructions = await MessageService.get_invite_instructions()
    
    await callback.message.edit_text(
        f"{success_text}{instructions}",
        parse_mode="Markdown"
    )
    await state.set_state(RegisterStates.waiting_for_invite)

@common_router.message(RegisterStates.waiting_for_invite)
async def handle_invite_input(message: types.Message, state: FSMContext):
    """Ученик переходит по ссылке-приглашению"""
    invite_code = message.text.strip()

    async for session in SessionService.get_session():
        try:
            # Регистрируем ученика через сервис
            student, relationship, tutor = await StudentService.register_by_invite(
                session=session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                invite_code=invite_code
            )
        
            success_text = await MessageService.get_connect_success_message(tutor)
        
            await message.answer(
                success_text,
                parse_mode="Markdown"
            )

            await NotificationService.notify_tutor_about_new_student(
                bot=message.bot,
                tutor_telegram_id=tutor.telegram_id,
                student_first_name=student.first_name or "Без имени",
                student_username=student.username
            )

            # Показываем меню ученика
            await message.answer(
                "Выберите действие:",
                reply_markup=student_main_menu()
            )
        
            await state.clear()

        except ValueError as e:
            await message.answer(f"❌ {str(e)}")

@common_router.callback_query(lambda c: c.data == "change_role_confirm")
async def handle_change_role_confirm(callback: types.CallbackQuery, state: FSMContext):
    """Запрос подтверждения смены роли"""
    await callback.answer()
    
    async for session in SessionService.get_session():
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.edit_text(MessageService.get_error_message("user_not_found"))
            return
        
        await callback.message.edit_text(
            text= await MessageService.get_change_role_confirm_message(user),
            reply_markup=confirm_change_role_menu()
        )

@common_router.callback_query(lambda c: c.data == "change_role_yes")
async def handle_change_role_yes(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение смены роли"""
    await callback.answer()
    
    
    async for session in SessionService.get_session():
        try:
            user = await UserService.get_user_by_telegram_id(
                session=session,
                telegram_id=callback.from_user.id
            )

            user = await UserService.change_role(
                session=session,
                user=user
            )
            
            # Получаем сообщение после смены роли
            text, keyboard, next_state = await MessageService.get_change_role_success_message(user)
            
            # Отправляем сообщение
            await callback.message.edit_text(
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            # Устанавливаем следующее состояние (если нужно)
            if next_state == "waiting_for_invite":
                await state.set_state(RegisterStates.waiting_for_invite)

        except ValueError as e:
            await callback.message.edit_text(f"❌ {str(e)}")
        
@common_router.callback_query(lambda c: c.data == "change_role_no")
async def handle_change_role_no(callback: types.CallbackQuery, state: FSMContext):
    """Отмена смены роли"""
    await callback.answer()
    
    async for session in SessionService.get_session():
        try: 
            user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
            
            if user:
                await handle_back_to_main(callback, state)

                # # Возвращаемся в меню настроек
                # await callback.message.edit_text(
                #     text="⚙️ **Настройки**",
                #     reply_markup=settings_menu(user.role),
                #     parse_mode="Markdown"
                # )
                
        except Exception as e:
            logging.error(f"Ошибка при отмене смены роли: {e}")
            await callback.message.edit_text(
                await MessageService.get_error_message("UNKNOWN_ERROR")
            )

@common_router.callback_query(lambda c: c.data == "back_to_main")
async def handle_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться в главное меню из настроек"""
    await callback.answer()
    
    async for session in SessionService.get_session():
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.edit_text(await MessageService.get_error_message("user_not_found"))
            return
        
        text, keyboard = await MessageService.get_main_mune_message(user)

        # Показываем соответствующее меню
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )

@common_router.callback_query(lambda c: c.data == "settings_menu")
async def handle_settings_menu(callback: types.CallbackQuery, state: FSMContext):
    """Открыть меню настроек"""
    print("BACK")
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