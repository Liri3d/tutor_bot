from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from keyboards import (
    settings_menu,
    tutor_menu_keyboard,
    build_students_keyboard,
    student_detail_menu
)

from db import tutor_crud, student_crud, Tutor
from keyboards import tutor_kb

from states import TutorStates
from services import *
from db import link_crud

tutor_router = Router()

@tutor_router.callback_query(lambda c: c.data == "tutor_add_student")
async def handle_tutor_add_student(callback: types.CallbackQuery, state: FSMContext):
    """Репетитор хочет добавить ученика - шаг 1: имя"""
    await callback.answer()
    
    # Проверяем, что пользователь - репетитор
    async for session in SessionService.get_session():
        tutor = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if not tutor:
            await callback.message.edit_text(
                "❌ Вы не зарегистрированы как репетитор.\n"
                "Нажмите /start для регистрации."
            )
            return
    
    await callback.message.edit_text(
        "👤 **Добавление ученика** (шаг 1 из 4)\n\n"
        "Введите **имя** ученика:\n\n"
        "❌ Для отмены нажмите /cancel",
        parse_mode="Markdown"
    )
    await state.set_state(TutorStates.waiting_for_student_name)

@tutor_router.message(TutorStates.waiting_for_student_name)
async def handle_student_name(message: types.Message, state: FSMContext):
    """Шаг 1: Получаем имя ученика"""
    name = message.text.strip()
    
    # Проверка на отмену
    if name.lower() == "/cancel":
        await message.answer("❌ Добавление ученика отменено.")
        await state.clear()
        await message.answer(
            "Выберите действие:",
            reply_markup=tutor_menu_keyboard()
        )
        return
    
    # Валидация
    if len(name) < 2:
        await message.answer(
            "❌ Имя должно содержать минимум 2 символа.\n\n"
            "Введите имя ученика или нажмите /cancel для отмены:"
        )
        return
    
    # Сохраняем имя
    await state.update_data(student_name=name)
    
    # Переходим к шагу 2 - пол
    await message.answer(
        "👤 **Добавление ученика** (шаг 2 из 4)\n\n"
        "Выберите **пол** ученика:",
        parse_mode="Markdown",
        reply_markup=tutor_kb.gender_keyboard()
    )
    await state.set_state(TutorStates.waiting_for_student_gender)


@tutor_router.callback_query(TutorStates.waiting_for_student_gender)
async def handle_student_gender(callback: types.CallbackQuery, state: FSMContext):
    """Шаг 2: Получаем пол ученика"""
    await callback.answer()
    
    gender_map = {
        "gender_male": "Мужской",
        "gender_female": "Женский"
    }
    
    gender = gender_map.get(callback.data)
    if not gender:
        await callback.message.answer("❌ Пожалуйста, выберите пол из предложенных вариантов.")
        return
    
    # Сохраняем пол
    await state.update_data(student_gender=gender)
    
    # Переходим к шагу 3 - возраст
    await callback.message.edit_text(
        "👤 **Добавление ученика** (шаг 3 из 4)\n\n"
        "Введите **возраст** ученика (число):\n\n"
        "❌ Для отмены нажмите /cancel",
        parse_mode="Markdown"
    )
    await state.set_state(TutorStates.waiting_for_student_age)


@tutor_router.message(TutorStates.waiting_for_student_age)
async def handle_student_age(message: types.Message, state: FSMContext):
    """Шаг 3: Получаем возраст ученика"""
    age_text = message.text.strip()
    
    # Проверка на отмену
    if age_text.lower() == "/cancel":
        await message.answer("❌ Добавление ученика отменено.")
        await state.clear()
        await message.answer(
            "Выберите действие:",
            reply_markup=tutor_menu_keyboard()
        )
        return
    
    # Валидация возраста
    try:
        age = int(age_text)
        if age < 1 or age > 120:
            await message.answer(
                "❌ Возраст должен быть от 1 до 120 лет.\n\n"
                "Введите возраст ученика или нажмите /cancel для отмены:"
            )
            return
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите число.\n\n"
            "Введите возраст ученика или нажмите /cancel для отмены:"
        )
        return
    
    # Сохраняем возраст
    await state.update_data(student_age=age)
    
    # Переходим к шагу 4 - предмет
    await message.answer(
        "👤 **Добавление ученика** (шаг 4 из 4)\n\n"
        "Введите **предмет**, который будет изучать ученик:\n"
        "(например: Немецкий, Английский, Математика)\n\n"
        "❌ Для отмены нажмите /cancel",
        parse_mode="Markdown"
    )
    await state.set_state(TutorStates.waiting_for_student_subject)


@tutor_router.message(TutorStates.waiting_for_student_subject)
async def handle_student_subject(message: types.Message, state: FSMContext):
    """Шаг 4: Получаем предмет и создаём ученика"""
    subject = message.text.strip()
    
    # Проверка на отмену
    if subject.lower() == "/cancel":
        await message.answer("❌ Добавление ученика отменено.")
        await state.clear()
        await message.answer(
            "Выберите действие:",
            reply_markup=tutor_menu_keyboard()
        )
        return
    
    # Валидация предмета
    if len(subject) < 2:
        await message.answer(
            "❌ Предмет должен содержать минимум 2 символа.\n\n"
            "Введите предмет или нажмите /cancel для отмены:"
        )
        return
    
    # Получаем все данные из состояния
    data = await state.get_data()
    student_name = data.get('student_name')
    student_gender = data.get('student_gender')
    student_age = data.get('student_age')
    
    try:
        async for session in SessionService.get_session():
            # Получаем репетитора
            tutor = await tutor_crud.get_by_telegram_id(session, message.from_user.id)
            if not tutor:
                await message.answer("❌ Репетитор не найден.")
                await state.clear()
                return
            
            # Создаём ученика
            student = await student_crud.create(
                session=session,
                student_name=student_name,
                gender=student_gender,
                age=student_age,
                subject=subject
            )
            
            # Привязываем ученика к репетитору
            link = await link_crud.create(
                session=session,
                tutor_id=tutor.id,
                student_id=student.id,
                status="active"
            )
            
            # Формируем сообщение об успехе
            await message.answer(
                f"✅ **Ученик успешно добавлен!**\n\n"
                f"📋 **Данные ученика:**\n"
                f"👤 Имя: {student.first_name}\n"
                f"⚧ Пол: {student.gender or 'Не указан'}\n"
                f"📅 Возраст: {student.age or 'Не указан'}\n"
                f"📖 Предмет: {student.subject or 'Не указан'}\n"
                f"🆔 ID: {student.id}\n\n",
                parse_mode="Markdown"
            )
            
            # Показываем меню
            await message.answer(
                "Выберите действие:",
                reply_markup=tutor_menu_keyboard()
            )
            
            await state.clear()
            
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании ученика: {str(e)}")
        await state.clear()


@tutor_router.callback_query(lambda c: c.data == "cancel_action")
async def handle_cancel_action(callback: types.CallbackQuery, state: FSMContext):
    """Отмена действия"""
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Действие отменено."
    )
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=tutor_menu_keyboard()
    )


async def _show_students_list(
    message_or_callback: types.Message | types.CallbackQuery,
    session,
    tutor: Tutor
) -> None:
    """
    Общая логика отображения списка учеников.
    Используется в handle_tutor_students и handle_back_to_tutor_students.
    
    Args:
        message_or_callback: Message или CallbackQuery для ответа
        session: Сессия БД
        tutor: Объект репетитора
    """
    students = await link_crud.get_students_for_tutor(session, tutor.id)
    
    if students:
        # Формируем текст со списком учеников
        text = "👥 **Ваши ученики:**\n\n"
        
        keyboard = build_students_keyboard(students, tutor.id)
        
        # Определяем, как отвечать - через message или callback
        if isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.edit_text(
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            await message_or_callback.answer(
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    else:
        empty_text = "👤 У вас пока нет учеников.\n\nНажмите ➕ Добавить ученика, чтобы добавить первого ученика."
        
        if isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.edit_text(
                text=empty_text,
                reply_markup=tutor_menu_keyboard()
            )
        else:
            await message_or_callback.answer(
                text=empty_text,
                reply_markup=tutor_menu_keyboard()
            )


@tutor_router.callback_query(lambda c: c.data == "tutor_students")
async def handle_tutor_students(callback: types.CallbackQuery, state: FSMContext):
    """Репетитор хочет просмотреть список учеников"""
    await callback.answer()
    await state.clear()

    async for session in SessionService.get_session():
        tutor = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if not tutor:
            await callback.message.edit_text(
                "❌ Вы не зарегистрированы как репетитор.\n"
                "Нажмите /start для регистрации."
            )
            return
        
        await _show_students_list(callback, session, tutor)

@tutor_router.callback_query(lambda c: c.data and c.data.startswith("student_"))
async def handle_student_click(callback: types.CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку ученика"""
    await callback.answer()
    
    # Извлекаем ID ученика из callback_data
    student_id = int(callback.data.split("_")[1])
    
    async for session in SessionService.get_session():
        tutor = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if not tutor:
            await callback.message.edit_text("❌ Вы не репетитор.")
            return
        
        # Получаем ученика
        student = await student_crud.get_by_id(session, student_id)
        if not student:
            await callback.message.edit_text("❌ Ученик не найден.")
            return
        
        # Проверяем, что ученик принадлежит этому репетитору
        link = await link_crud.get_by_tutor_and_student(session, tutor.id, student.id)
        if not link:
            await callback.message.edit_text("❌ Этот ученик не принадлежит вам.")
            return
        
        # Формируем полную информацию об ученике
        info_text = (
            f"📋 **Информация об ученике**\n\n"
            f"👤 **Имя:** {student.student_name or student.first_name or 'Не указано'}\n"
            f"⚧ **Пол:** {student.gender or 'Не указан'}\n"
            f"📅 **Возраст:** {student.age or 'Не указан'} лет\n"
            f"📖 **Предмет:** {student.subject or 'Не указан'}\n"
            f"🆔 **ID:** {student.id}\n"
            f"📱 **Telegram:** {('@' + student.username) if student.username else 'Не подключён'}\n"
            f"📅 **Зарегистрирован:** {student.registered_at.strftime('%d.%m.%Y %H:%M') if student.registered_at else 'Неизвестно'}\n"
            f"📊 **Статус:** {'✅ Активен' if link.status == 'active' else '⏸ Приостановлен' if link.status == 'paused' else '❌ Неактивен'}\n"
        )
        
        # Добавляем информацию о Telegram ID если есть
        if student.telegram_id:
            info_text += f"🆔 **Telegram ID:** {student.telegram_id}\n"
        
        await callback.message.edit_text(
            text=info_text,
            parse_mode="Markdown",
            reply_markup=student_detail_menu(student_id)
        )

@tutor_router.callback_query(lambda c: c.data == "back_to_tutor_students")
async def handle_back_to_tutor_students(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к списку учеников"""
    await callback.answer()
    await state.clear()

    async for session in SessionService.get_session():
        tutor = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if not tutor:
            await callback.message.edit_text("❌ Вы не репетитор.")
            return
        
        await _show_students_list(callback, session, tutor)