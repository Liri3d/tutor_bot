from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
import logging

from states import RegisterStates
from keyboards.inline import role_keyboard
from db.session import get_session
from db.crud import (
    get_user_by_telegram_id,
    create_user,
    get_invite_by_code,
    get_relationship,
    create_relationship,
    get_user_by_id,
    mark_invite_as_used,
)

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

    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)

        if invite_code:
            # Проверяем приглашение
            invite = await get_invite_by_code(session, invite_code)

            if not invite:
                await message.answer(
                    "❌ Недействительный код приглашения.\n\n"
                    "Код мог быть неверным, использованным или истекшим.\n"
                    "Пожалуйста, проверьте код и попробуйте снова."
                )
                return

            # Проверяем, не пытается ли пользователь подключиться к самому себе
            tutor = await get_user_by_id(session, invite.tutor_id)
            if tutor and tutor.telegram_id == message.from_user.id:
                await message.answer(
                    "❌ Нельзя подключиться к самому себе!"
                )
                return
            
            # Проверяем, что пользователь ещё не зарегистрирован
            if user:
                # Случай 1: Пользователь — репетитор
                if user.role == "tutor":
                    await message.answer(
                        "❌ Вы уже зарегистрированы как репетитор.\n\nЧтобы подключиться к другому репетитору как ученик, ",
                        "смените свою роль в настройках: '/settings' → 'Сменить роль на ученика'",
                        # "Если вы хотите подключиться к другому репетитору, обратитесь к нему за новым приглашением."
                        parse_mode="Markdown"
                    )
                    return
                # Случай 2: Пользователь — ученик
                if user.role == "student":
                    # Проверяем, не подключён ли уже к этому репетитору
                    existing_relationship = await get_relationship(
                        session,
                        invite.tutor_id,
                        user.id
                    )
                    
                    if existing_relationship:
                        await message.answer(
                            f"✅ Вы уже подключены к репетитору {tutor.first_name or 'репетитору'}!"
                        )
                        await message.answer(
                            "Выберите действие:",
                            reply_markup=student_main_menu()
                        )
                        return
                    
                    # Подключаем существующего ученика к новому репетитору
                    relationship = await create_relationship(
                        session=session,
                        tutor_id=invite.tutor_id,
                        student_id=user.id
                    )
                    
                    # Отмечаем приглашение как использованное
                    await mark_invite_as_used(session, invite, user.telegram_id)
                    
                    await message.answer(
                        f"✅ Вы успешно подключились к репетитору {tutor.first_name or 'репетитору'}!"
                    )
                    
                    # Уведомляем репетитора
                    try:
                        await message.bot.send_message(
                            tutor.telegram_id,
                            f"🎉 К вам подключился новый ученик!\n\n"
                            f"👤 {user.first_name or 'Без имени'}"
                            f"{' (@' + user.username + ')' if user.username else ''}"
                        )
                    except Exception as e:
                        logging.error(f"Не удалось уведомить репетитора: {e}")
                    
                    await message.answer(
                        "Выберите действие:",
                        reply_markup=student_main_menu()
                    )
                    
                    await state.clear()
                    return
        

                # Случай 3: Пользователь не зарегистрирован — создаём
                student = await create_user(
                    session=session,
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    role="student"
                )
                
                # Создаём связь
                relationship = await create_relationship(
                    session=session,
                    tutor_id=invite.tutor_id,
                    student_id=student.id
                )
                
                # Отмечаем приглашение как использованное
                await mark_invite_as_used(session, invite, student.telegram_id)
                
                # Уведомляем ученика
                await message.answer(
                    f"✅ Вы успешно подключились к репетитору **{tutor.first_name or 'репетитору'}**!\n\n"
                    "Теперь вы можете просматривать свои занятия и баланс.",
                    parse_mode="Markdown"
                )
                
                # Уведомляем репетитора
                try:
                    await message.bot.send_message(
                        tutor.telegram_id,
                        f"🎉 К вам подключился новый ученик!\n\n"
                        f"👤 {student.first_name or 'Без имени'}"
                        f"{' (@' + student.username + ')' if student.username else ''}"
                    )
                except Exception as e:
                    logging.error(f"Не удалось уведомить репетитора: {e}")
                
                # Показываем меню ученика
                await message.answer(
                    "Выберите действие:",
                    reply_markup=student_main_menu()
                )
                
                await state.clear()
                return
                        
            # Создаём ученика
            student = await create_user(
                session=session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                role="student"
            )
            
            # Создаём связь
            relationship = await create_relationship(
                session=session,
                tutor_id=invite.tutor_id,
                student_id=student.id
            )
            
            # Отмечаем приглашение как использованное
            await mark_invite_as_used(session, invite, student.telegram_id)
            
            # Уведомляем ученика
            await message.answer(
                f"✅ Вы успешно подключились к репетитору {tutor.first_name or 'репетитору'}!\n\n"
                "Теперь вы можете просматривать свои занятия и баланс.",
                parse_mode="Markdown"
            )
            
            # Уведомляем репетитора
            try:
                await message.bot.send_message(
                    tutor.telegram_id,
                    f"🎉 К вам подключился новый ученик!\n\n"
                    f"👤 {student.first_name or 'Без имени'}"
                    f"{' (@' + student.username + ')' if student.username else ''}"
                )
            except Exception as e:
                logging.error(f"Не удалось уведомить репетитора: {e}")
            
            # Показываем меню ученика
            await message.answer(
                "Выберите действие:",
                reply_markup=student_main_menu()
            )
            
            await state.clear()
            return

        # Если пользователь уже зарегистрирован
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

        # Если пользователь не зарегистрирован и нет кода — предлагаем выбрать роль
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




@common_router.message(RegisterStates.waiting_for_invite)
async def handle_invite_input(message: types.Message, state: FSMContext):
    """Ученик вводит код приглашения"""
    invite_code = message.text.strip()
    
    async for session in get_session():
        # Проверяем приглашение
        invite = await get_invite_by_code(session, invite_code)
        
        if not invite:
            await message.answer(
                "❌ Недействительный код.\n\n"
                "Проверьте код и попробуйте снова."
            )
            return
        
        # Проверяем, не зарегистрирован ли уже ученик
        existing_user = await get_user_by_telegram_id(
            session, 
            message.from_user.id
        )
        
        if existing_user:
            # Если уже ученик, проверяем связь
            if existing_user.role == "student":
                relationship = await get_relationship(
                    session, 
                    invite.tutor_id, 
                    existing_user.id
                )
                if relationship:
                    await message.answer(
                        "✅ Вы уже подключены к этому репетитору!"
                    )
                    await state.clear()
                    return
            
            # Если репетитор пытается стать учеником
            if existing_user.role == "tutor":
                await message.answer(
                    "❌ Вы зарегистрированы как репетитор.\n"
                    "Репетитор не может подключиться как ученик."
                )
                return
        
        # Проверяем, что ученик не создан в БД
        # Если нет — создаём
        student = await get_user_by_telegram_id(session, message.from_user.id)
        if not student:
            student = await create_user(
                session=session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                role="student"
            )
        
        # Создаём связь
        relationship = await create_relationship(
            session=session,
            tutor_id=invite.tutor_id,
            student_id=student.id
        )
        
        # Отмечаем приглашение как использованное
        await mark_invite_as_used(session, invite, student.telegram_id)
        
        # Уведомления
        tutor = await get_user_by_id(session, invite.tutor_id)
        
        await message.answer(
            f"✅ Вы успешно подключились к репетитору!\n"
            f"👤 {tutor.first_name or 'Репетитор'}"
        )
        
        # Уведомляем репетитора
        try:
            await message.bot.send_message(
                tutor.telegram_id,
                f"🎉 Ученик подключился!\n\n"
                f"👤 Имя: {student.first_name or 'Без имени'}\n"
                f"🔗 Код: {invite.code}"
            )
        except Exception:
            pass
        
        # Показываем меню ученика
        await message.answer(
            "Выберите действие:",
            reply_markup=student_main_menu()
        )
        
        await state.clear()

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