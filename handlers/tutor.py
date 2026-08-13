from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from keyboards import (
    settings_menu,
    tutor_menu_keyboard,
    build_students_keyboard,
    build_students_for_lesson_keyboard,
    student_detail_menu,

    date_range_keyboard,
    time_range_keyboard,

    tutor_shedule_keyboard
)

from db import Tutor, tutor_crud, student_crud, link_crud, lesson_crud 
from states import TutorStates
from services import *
from keyboards import tutor_kb

tutor_router = Router()

@tutor_router.callback_query(lambda c: c.data == "tutor_add_lesson")
async def handle_tutor_add_lesson(callback: types.CallbackQuery, state: FSMContext):
    """
    Добавление урока
    Шаг 1: Репетитор выбирает ученика для занятия.
    Показываем список его учеников.
    """
    await callback.answer()
    
    async for session in SessionService.get_session():
        # Проверяем, что пользователь - репетитор
        tutor = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if not tutor:
            await callback.message.edit_text(
                "❌ Вы не зарегистрированы как репетитор.\n"
                "Нажмите /start для регистрации."
            )
            return
        
        # Получаем список учеников репетитора
        students = await link_crud.get_students_for_tutor(session, tutor.id)
        
        if not students:
            await callback.message.edit_text(
                "❌ У вас нет учеников.\n\n"
                "Сначала добавьте ученика через '➕ Добавить ученика'.",
                reply_markup=tutor_menu_keyboard()
            )
            return
        
        # Сохраняем ID репетитора в состояние
        await state.update_data(tutor_id=tutor.id)
        
        # Показываем список учеников кнопками
        await callback.message.edit_text(
            "👤 **Выберите ученика для занятия:**",
            parse_mode="Markdown",
            reply_markup=build_students_for_lesson_keyboard(students)  # ← новая клавиатура
        )

@tutor_router.callback_query(lambda c: c.data and c.data.startswith("lesson_select_student_"))
async def handle_lesson_student_select(callback: types.CallbackQuery, state: FSMContext):
    """Выбор ученика для занятия"""
    await callback.answer()
    
    # Извлекаем ID ученика
    student_id = int(callback.data.split("_")[3])
    await state.update_data(lesson_student_id=student_id)
    
    # Получаем имя ученика
    async for session in SessionService.get_session():
        student = await student_crud.get_by_id(session, student_id)
        if not student:
            await callback.message.edit_text("❌ Ученик не найден.")
            return
        
        student_name = student.student_name or student.first_name
        await state.update_data(lesson_student_name=student_name)
        
        await callback.message.edit_text(
            f"📅 **Шаг 2: Выберите дату занятия**\n\n"
            f"👤 Ученик: {student_name}\n\n"
            "❌ Для отмены введите /cancel",
            parse_mode="Markdown"
        )
        await state.set_state(TutorStates.waiting_lesson_date)

@tutor_router.message(TutorStates.waiting_lesson_date)
async def handle_lesson_date(message: types.Message, state: FSMContext):
    """
    Шаг 2: Показываем выбор даты (только кнопки).
    Если пользователь что-то пишет - напоминаем, что нужно выбрать кнопкой.
    """
    # Если пользователь что-то ввел текстом - игнорируем и напоминаем
    if message.text:
        await message.answer(
            "📅 **Пожалуйста, выберите дату из предложенных кнопок ниже.**\n\n"
            "❌ Для отмены нажмите /cancel",
            parse_mode="Markdown",
            reply_markup=date_range_keyboard()
        )

@tutor_router.callback_query(lambda c: c.data and c.data.startswith("date_"))
async def handle_date_selection(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик выбора даты из inline-кнопок.
    """
    await callback.answer()
    
    # Извлекаем дату из callback_data
    parts = callback.data.split("_")
    if len(parts) != 4:
        await callback.message.edit_text("❌ Ошибка: неверный формат даты.")
        return
    
    try:
        day = int(parts[1])
        month = int(parts[2])
        year = int(parts[3])
        
        date = datetime(year, month, day).date()
        
        # Проверяем, что дата не в прошлом
        if date < datetime.now().date():
            await callback.message.edit_text(
                "❌ Эта дата уже прошла.\n\n"
                "Выберите другую:",
                reply_markup=date_range_keyboard()
            )
            return
        
        # Сохраняем дату
        await state.update_data(lesson_date=date)
        
        # Получаем имя ученика
        data = await state.get_data()
        student_name = data.get("lesson_student_name", "ученик")
        
        # Переходим к шагу 3 - время
        await callback.message.edit_text(
            f"✅ Дата выбрана: {date.strftime('%d.%m.%Y')}\n\n"
            f"👤 Ученик: {student_name}\n\n"
            "⏰ **Шаг 3: Выберите время занятия**\n\n"
            "❌ Для отмены введите /cancel",
            parse_mode="Markdown",
            reply_markup=time_range_keyboard()  
        )
       
    except ValueError:
        await callback.message.edit_text("❌ Ошибка: неверный формат даты.")

@tutor_router.callback_query(lambda c: c.data and c.data.startswith("time_"))
async def handle_time_selection(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик выбора времени из inline-кнопок.
    После выбора времени переходим к вводу темы.
    """
    await callback.answer()
    
    # Извлекаем время из callback_data
    # Формат: time_14_00
    parts = callback.data.split("_")
    if len(parts) != 3:
        await callback.message.edit_text("❌ Ошибка: неверный формат времени.")
        return
    
    try:
        hour = int(parts[1])
        minute = int(parts[2])
        
        # Получаем дату из состояния
        data = await state.get_data()
        date = data.get("lesson_date")
        student_name = data.get("lesson_student_name", "ученик")
        
        if not date:
            await callback.message.edit_text(
                "❌ Ошибка: дата не выбрана. Начните заново.",
                reply_markup=tutor_menu_keyboard()
            )
            return
        
        # Создаём полную дату и время
        start_time = datetime.combine(date, datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time())
        
        # Проверяем, что время не в прошлом
        if start_time < datetime.now():
            await callback.message.edit_text(
                "❌ Это время уже прошло.\n\n"
                "Выберите другое время:",
                reply_markup=time_range_keyboard()
            )
            return
        
        # Сохраняем время
        await state.update_data(lesson_start_time=start_time)
        
        # Переходим к шагу 4 - тема
        await callback.message.edit_text(
            f"✅ Время выбрано: {start_time.strftime('%H:%M')}\n\n"
            f"👤 Ученик: {student_name}\n"
            f"📅 Дата: {date.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {start_time.strftime('%H:%M')}\n\n"
            "📖 **Шаг 4: Введите тему занятия (необязательно)**\n\n"
            "Можете ввести тему или нажмите /skip чтобы пропустить.\n\n"
            "❌ Для отмены введите /cancel",
            parse_mode="Markdown"
        )
        await state.set_state(TutorStates.waiting_lesson_title)
        
    except ValueError:
        await callback.message.edit_text("❌ Ошибка: неверный формат времени.")

@tutor_router.message(TutorStates.waiting_lesson_title)
async def handle_lesson_title(message: types.Message, state: FSMContext):
    """
    Шаг 4: Получаем тему и создаём урок.
    """
    title = message.text.strip()
    
    # Проверяем отмену
    if title.lower() == "/cancel":
        await message.answer("❌ Создание урока отменено.")
        await state.clear()
        await message.answer("Выберите действие:", reply_markup=tutor_menu_keyboard())
        return
    
    # Если /skip - пропускаем тему
    if title.lower() == "/skip":
        title = None
    
    # Получаем все данные из состояния
    data = await state.get_data()
    tutor_id = data.get("tutor_id")
    student_id = data.get("lesson_student_id")
    student_name = data.get("lesson_student_name")
    start_time = data.get("lesson_start_time")
    
    # Проверяем, что все данные есть
    if not tutor_id or not student_id or not start_time:
        await message.answer(
            "❌ Ошибка: не все данные заполнены. Начните создание урока заново.",
            reply_markup=tutor_menu_keyboard()
        )
        await state.clear()
        return
    
    try:
        async for session in SessionService.get_session():
            # Проверяем, что репетитор существует
            tutor = await tutor_crud.get_by_id(session, tutor_id)
            if not tutor:
                await message.answer("❌ Репетитор не найден.")
                await state.clear()
                return
            
            # ===== СОЗДАЁМ УРОК! 🎉 =====
            lesson = await lesson_crud.create(
                session=session,
                tutor_id=tutor_id,
                student_id=student_id,
                start_time=start_time,
                duration_minutes=60,  # ← пока 60 минут, можно будет добавить выбор
                title=title,
                status="scheduled"
            )
            
            # Форматируем дату для вывода
            date_str = start_time.strftime("%d.%m.%Y")
            time_str = start_time.strftime("%H:%M")
            
            # Сообщение об успехе
            success_text = (
                f"✅ **Урок успешно создан!** 🎉\n\n"
                f"📋 **Детали урока:**\n"
                f"👤 Ученик: {student_name}\n"
                f"📅 Дата: {date_str}\n"
                f"⏰ Время: {time_str}\n"
                f"⏱ Длительность: 60 мин\n"
            )
            if title:
                success_text += f"📖 Тема: {title}\n"
            success_text += f"\n🆔 ID урока: `{lesson.id}`"
            
            await message.answer(
                success_text,
                parse_mode="Markdown",
                reply_markup=tutor_menu_keyboard()
            )
            
            # Очищаем состояние
            await state.clear()
            
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании урока: {str(e)}")
        await state.clear()











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
                f"👤 Имя: {student.student_name or student.first_name}\n"
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
            f"👤 {student.student_name or 'Не указано'} ({student.first_name or student.username or ''}) "
            f"{'М' if student.gender == 'Мужской' else 'Ж'}\n"
            f"{student.age or 'Не указан'} лет\n"
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
        
        await message_or_callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
       
    else:
        empty_text = "👤 У вас пока нет учеников.\n\nНажмите ➕ Добавить ученика, чтобы добавить первого ученика."
        
        await message_or_callback.message.edit_text(
            text=empty_text,
            reply_markup=tutor_menu_keyboard()
        )













@tutor_router.callback_query(lambda c: c.data == "tutor_schedule")
async def handle_tutor_schedule(callback: types.CallbackQuery, state: FSMContext):
    """
    Показать расписание репетитора.
    """
    await callback.answer()
    await state.clear()
    
    async for session in SessionService.get_session():
        # Проверяем, что пользователь - репетитор
        tutor = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if not tutor:
            await callback.message.edit_text(
                "❌ Вы не зарегистрированы как репетитор.\n"
                "Нажмите /start для регистрации."
            )
            return
        
        # Получаем занятия на ближайшие 7 дней
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_later = today + timedelta(days=7)
        
        lessons = await LessonService.get_tutor_lessons(
            session=session,
            tutor_id=tutor.id,
            start_date=today,
            end_date=week_later,
            status="scheduled",
            limit=50
        )
        
        if not lessons:
            await callback.message.edit_text(
                "📅 У вас нет запланированных занятий на ближайшую неделю.\n\n"
                "Нажмите ➕ Добавить занятие, чтобы создать новое.",
                reply_markup=tutor_menu_keyboard()
            )
            return
        
        # Формируем сообщение с расписанием
        text = "📅 **Ваше расписание на неделю:**\n\n"
        
        # Группируем занятия по дням
        from collections import defaultdict
        lessons_by_day = defaultdict(list)
        for lesson in lessons:
            day_key = lesson.start_time.strftime("%d.%m.%Y")
            lessons_by_day[day_key].append(lesson)
        
        # Выводим занятия по дням
        for day_key in sorted(lessons_by_day.keys()):
            day_lessons = lessons_by_day[day_key]
            # Название дня недели
            day_date = datetime.strptime(day_key, "%d.%m.%Y")
            weekday = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][day_date.weekday()]
            text += f"\n📌 *{day_key} ({weekday})*\n"
            
            for lesson in day_lessons:
                # Получаем имя ученика
                student = await student_crud.get_by_id(session, lesson.student_id)
                student_name = student.student_name or student.first_name or "Ученик"
                
                time_str = lesson.start_time.strftime("%H:%M")
                text += f"   ⏰ {time_str} - {student_name}"
                if lesson.title:
                    text += f" ({lesson.title})"
                text += f" [ID: {lesson.id}]\n"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=tutor_shedule_keyboard()
        )


@tutor_router.callback_query(lambda c: c.data == "tutor_all_lessons")
async def handle_tutor_all_lessons(callback: types.CallbackQuery, state: FSMContext):
    """
    Показать все занятия репетитора (без фильтра по дате).
    """
    await callback.answer()
    await state.clear()
    
    async for session in SessionService.get_session():
        tutor = await tutor_crud.get_by_telegram_id(session, callback.from_user.id)
        if not tutor:
            await callback.message.edit_text("❌ Вы не репетитор.")
            return
        
        # Получаем все активные занятия
        lessons = await LessonService.get_tutor_lessons(
            session=session,
            tutor_id=tutor.id,
            status="scheduled",
            limit=50
        )
        
        if not lessons:
            await callback.message.edit_text(
                "📅 У вас нет запланированных занятий.",
                reply_markup=tutor_menu_keyboard()
            )
            return
        
        text = "📋 **Все запланированные занятия:**\n\n"
        for idx, lesson in enumerate(lessons[:20], 1):
            student = await student_crud.get_by_id(session, lesson.student_id)
            student_name = student.student_name or student.first_name or "Ученик"
            date_str = lesson.start_time.strftime("%d.%m.%Y %H:%M")
            text += f"{idx}. {date_str} - {student_name}"
            if lesson.title:
                text += f" ({lesson.title})"
            text += f"\n"
        
        if len(lessons) > 20:
            text += f"\n... и ещё {len(lessons) - 20} занятий"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=tutor_menu_keyboard()
        )