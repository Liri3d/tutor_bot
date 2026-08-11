from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
import logging


from states import RegisterStates
from keyboards import (
    role_keyboard,
    start_menu_keyboard,
    student_menu_keyboard,
    tutor_menu_keyboard,

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
        tutor = await tutor_crud.get_by_telegram_id(session, message.from_user.id)

        if invite_code:
            # try:
            #     # Регистрируем ученика по инвайту
            #     student, tutor = await StudentService.register_by_invite(
            #         session=session,
            #         telegram_id=message.from_user.id,
            #         username=message.from_user.username,
            #         first_name=message.from_user.first_name,
            #         invite_code=invite_code
            #     )

            #     success_text = await MessageService.get_registration_success_message(
            #         student, "student"
            #     )
            #     await message.answer(success_text,
            #                          parse_mode="Markdown",
            #                          reply_markup=student_menu_keyboard())
                
            #     await NotificationService.notify_tutor_about_new_student(
            #         bot=message.bot,
            #         tutor_telegram_id=tutor.telegram_id,
            #         student_first_name=student.first_name or "Без имени",
            #         student_username=student.username
            #     )
                
            #     await message.answer(
            #         "Выберите действие:",
            #         reply_markup=student_menu_keyboard()
            #     )
                
            #     await state.clear()
            #     return

            # except ValueError as e:
            #     await message.answer(f"❌ {str(e)}")
            #     return
                   
            # TODO
            pass
        
        # Если пользователь уже зарегистрирован как ученик
        if student:
            welcome_text = f"👋 С возвращением, {student.first_name or 'ученик'}!\n\nВыберите действие:"
            await message.answer(
                welcome_text,
                reply_markup=student_menu_keyboard()  
            )
            return

        # Если пользователь уже зарегистрирован как репетитор
        if tutor:
            welcome_text = f"👋 С возвращением, {tutor.first_name or 'репетитор'}!\n\nВыберите действие:"
            await message.answer(
                welcome_text,
                reply_markup=tutor_menu_keyboard()  
            )
            return
        
        # Если пользователь не зарегистрирован — показываем кнопку Старт
        await state.set_state(RegisterStates.waiting_for_role)
        await message.answer(
            "👋 Добро пожаловать в Tutor Bot!\n\n"
            "Я помогу вам управлять расписанием и учениками.\n\n"
            "Нажмите кнопку '🚀 Старт', чтобы начать:",
            reply_markup=start_menu_keyboard()  # ← показываем кнопку Старт
        )

@common_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Справка по командам бота"""
    help_text = (
        "🤖 Помощь по Tutor Bot\n\n"  # ← * вместо ** для Markdown
    )
    await message.answer(help_text, parse_mode="Markdown")

@common_router.message(lambda message: message.text == "🚀 Старт")
async def handle_start_button(message: types.Message, state: FSMContext):
    """Обработчик нажатия на кнопку '🚀 Старт'"""
    await state.clear()
    
    async for session in SessionService.get_session():
        # Проверяем, есть ли пользователь в БД
        student = await student_crud.get_by_telegram_id(session, message.from_user.id)
        tutor = await tutor_crud.get_by_telegram_id(session, message.from_user.id)
        
        # Если ученик
        if student:
            await message.answer(
                f"👋 С возвращением, {student.first_name or 'ученик'}!\n\nВыберите действие:",
                reply_markup=student_menu_keyboard()
            )
            return
        
        # Если репетитор
        if tutor:
            await message.answer(
                f"👋 С возвращением, {tutor.first_name or 'репетитор'}!\n\nВыберите действие:",
                reply_markup=tutor_menu_keyboard()
            )
            return
        
        # Если не зарегистрирован - предлагаем выбрать роль
        await state.set_state(RegisterStates.waiting_for_role)
        await message.answer(
            "👋 Добро пожаловать в Tutor Bot!\n\n"
            "Я помогу вам управлять расписанием и учениками.\n\n"
            "Вы ученик или репетитор?",
            reply_markup=role_keyboard()  # ← показываем инлайн-кнопки выбора роли
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
                reply_markup=tutor_menu_keyboard()
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
        reply_markup=tutor_menu_keyboard()
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
                reply_markup=tutor_menu_keyboard()
            )
            await state.clear()
            return
        
        student = await student_crud.get_by_telegram_id(session, callback.from_user.id)
        if student:
            # Если ученик - показываем меню ученика
            await callback.message.edit_text(
                "👋 Главное меню ученика:\n\n"
                "Выберите действие:",
                reply_markup=student_menu_keyboard()
            )
            await state.clear()
            return
        
        # Если пользователь не найден
        await callback.message.edit_text(
            "❌ Пользователь не найден.\n"
            "Нажмите /start для регистрации."
        )

@common_router.message(lambda message: message.text == "🔙 В главное меню")
async def handle_back_to_main_button(message: types.Message, state: FSMContext):
    """Возврат в главное меню по reply-кнопке"""
    await state.clear()
    
    async for session in SessionService.get_session():
        # Проверяем, кто пользователь
        tutor = await tutor_crud.get_by_telegram_id(session, message.from_user.id)
        if tutor:
            await message.answer(
                "👋 Главное меню репетитора:",
                reply_markup=tutor_menu_keyboard()
            )
            return
        
        student = await student_crud.get_by_telegram_id(session, message.from_user.id)
        if student:
            await message.answer(
                "👋 Главное меню ученика:",
                reply_markup=student_menu_keyboard()
            )
            return
        
        # Если не найден
        await message.answer(
            "❌ Пользователь не найден.",
            reply_markup=start_menu_keyboard()
        )