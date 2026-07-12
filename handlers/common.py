from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

from states.register_states import RegisterStates
from keyboards.inline import role_keyboard
from db.session import get_session
from db.crud import get_user_by_telegram_id, create_user

from keyboards import (
    tutor_main_menu,
    student_main_menu,
    settings_menu,
    confirm_change_role_menu,
    
)

common_router = Router()

@common_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text="Загрузка...",
        reply_markup=ReplyKeyboardRemove()
    )

    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)

        if user:
            if user.role == "tutor":
                await message.answer(
                    f"👋 С возвращением, {user.first_name or 'репетитор'}!\n\nВыберите действие:",
                    reply_markup=tutor_main_menu()
                )
                return
            else:
                await message.answer(
                    f"👋 С возвращением, {user.first_name or 'ученик'}!\n\nВыберите действие:",
                    reply_markup=student_main_menu()
                )
                return

    await state.set_state(RegisterStates.waiting_for_role)
    await message.answer(
        "👋 Добро пожаловать в Tutor Bot!\n\n"
        "Я помогу вам управлять своим расписанием.\n\n"
        "Вы ученик или репетитор?",
        reply_markup=role_keyboard()
    )

@common_router.callback_query(lambda c: c.data == "role_tutor")
async def handle_role_tutor(callback: types.CallbackQuery, state: FSMContext):
    """Пользователь выбрал роль репетитора"""
    await callback.answer() 
    
    # Сохраняем пользователя в БД
    async for session in get_session():
        user = await create_user(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            role="tutor"
        )

    await callback.message.edit_text(
        "✅ Вы зарегистрированы как репетитор!\n\nВыберите действие:"
    )
    await callback.message.answer(
        "Меню репетитора:",
        reply_markup=tutor_main_menu()
    )

@common_router.callback_query(lambda c: c.data == "role_student")
async def handle_role_student(callback: types.CallbackQuery, state: FSMContext):
    """Пользователь выбрал роль ученика"""
    await callback.answer()
    
    async for session in get_session():
        user = await create_user(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            role="student"
        )

    await callback.message.edit_text(
        "👨‍🎓 Чтобы подключиться,\n"
        "введите код приглашения от репетитора:\n\n"
        "Например: `/invite ABC123`"
    )

    await state.set_state(RegisterStates.waiting_for_invite)






# @common_router.message(RegisterStates.waiting_for_invite)
# async def handle_invite_input(message: types.Message, state: FSMContext):
#     """Пользователь ввел инвайт-код"""
#     invite_code = message.text.strip()
    
#     await message.answer(
#         f"🔑 Вы ввели код: `{invite_code}`\n\n"
#         "Позже мы добавим проверку кода и подключение к репетитору."
#     )
    
#     await message.answer(
#         "Вы успешно подключились к репетитору!\n\n"
#         "Выберите действие:",
#         reply_markup=student_main_menu()
#     )

#     await state.clear()














@common_router.callback_query(lambda c: c.data == "change_role_confirm")
async def handle_change_role_confirm(callback: types.CallbackQuery, state: FSMContext):
    """Запрос подтверждения смены роли"""
    await callback.answer()
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден.")
            return
        
        new_role = "ученика" if user.role == "tutor" else "репетитора"
        
        await callback.message.edit_text(
            text=f"⚠️ Вы уверены, что хотите сменить роль на {new_role}?\n\n"
                 f"При смене роли вы потеряете доступ к данным, связанным со старой ролью.",
            reply_markup=confirm_change_role_menu()
        )

@common_router.callback_query(lambda c: c.data == "change_role_yes")
async def handle_change_role_yes(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение смены роли"""
    await callback.answer()
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден.")
            return
        
        # Меняем роль
        new_role = "tutor" if user.role == "student" else "student"
        old_role = user.role
        user.role = new_role
        await session.commit()
        
        user = await get_user_by_telegram_id(session, callback.from_user.id)

        # Показываем новое меню
        if user.role == "tutor":
            await callback.message.edit_text(
                text=f"✅ Вы сменили роль с {old_role} на {new_role}!\n\nВыберите действие:",
                reply_markup=tutor_main_menu()
            )
        else:
            await callback.message.edit_text(
                text=f"✅ Вы сменили роль с {old_role} на {new_role}!\n\nТеперь введите код приглашения от репетитора:"
            )
            await state.set_state(RegisterStates.waiting_for_invite)

@common_router.callback_query(lambda c: c.data == "change_role_no")
async def handle_change_role_no(callback: types.CallbackQuery, state: FSMContext):
    """Отмена смены роли"""
    await callback.answer()
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        
        if user:
            # Возвращаемся в меню настроек
            await callback.message.edit_text(
                text="⚙️ Настройки",
                reply_markup=settings_menu(user.role)
            )