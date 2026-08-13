from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

from db import Student

def tutor_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню репетитора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Моё расписание", callback_data="tutor_schedule")],
            [InlineKeyboardButton(text="➕ Добавить занятие", callback_data="tutor_add_lesson")],
            [InlineKeyboardButton(text="👥 Мои ученики", callback_data="tutor_students")],
            [InlineKeyboardButton(text="➕ Добавить ученика", callback_data="tutor_add_student")],
            # [InlineKeyboardButton(text="🔗 Пригласить ученика", callback_data="tutor_invite")],
            # [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings_menu")],
        ]
    )

def tutor_shedule_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📋 Все занятия",
                callback_data="tutor_all_lessons"
            )],
            [InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_main"
            )],
        ]
    )
    

def date_range_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт inline-клавиатуру с датами на 14 дней вперед.
    """
    builder = InlineKeyboardBuilder()
    
    today = datetime.now().date()
    
    # Названия дней недели
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    
    # Добавляем 14 дней вперед (2 недели)
    for i in range(14):
        date = today + timedelta(days=i)
        day_num = date.day
        month_num = date.month
        year_num = date.year
        
        # Определяем день недели
        weekday = weekdays[date.weekday()]
        
        # Формируем текст кнопки: "15.08 (Чт)"
        button_text = f"{day_num:02d}.{month_num:02d} ({weekday})"
        
        # Callback_data: "date_15_08_2026"
        callback_data = f"date_{day_num:02d}_{month_num:02d}_{year_num}"
        
        # Если это сегодня - помечаем
        if i == 0:
            button_text = f"🟢 {button_text}"
        
        builder.button(
            text=button_text,
            callback_data=callback_data
        )
    
    # Располагаем по 2 кнопки в строке
    builder.adjust(2)
    
    # Добавляем кнопки управления
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")
    )
    
    return builder.as_markup()

def time_range_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт inline-клавиатуру с выбором времени с 8:00 до 21:00.
    Каждый час - одна кнопка.
    """
    builder = InlineKeyboardBuilder()
    
    # Время с 8:00 до 21:00
    for hour in range(8, 22):  # 8, 9, 10, ... 21
        time_str = f"{hour:02d}:00"
        builder.button(
            text=time_str,
            callback_data=f"time_{hour:02d}_00"
        )
    
    # Располагаем по 4 кнопки в строке
    builder.adjust(4)
    
    # Добавляем кнопку отмены
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")
    )
    
    return builder.as_markup()

def gender_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора пола"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male"),
                InlineKeyboardButton(text="👩 Женский", callback_data="gender_female")
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")]
        ]
    )

def build_students_keyboard(students: list[Student], tutor_id: int) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру со списком учеников.
    Каждая кнопка — это ученик, callback_data содержит его ID.
    """
    builder = InlineKeyboardBuilder()
    
    for student in students:
        # Формируем текст кнопки: имя + username (если есть)
        button_text = student.student_name or student.first_name or student.username
        if student.username:
            button_text += f" (@{student.username})"
        
        # Добавляем кнопку с callback_data, содержащим ID ученика
        builder.button(
            text=button_text,
            callback_data=f"student_{student.id}"  # Уникальный идентификатор
        )

    builder.button(
            text="➕ Добавить ученика",
            callback_data="tutor_add_student"
        )
                
    # Добавляем кнопку "Назад" в меню репетитора
    builder.button(
        text="🔙 Назад",
        callback_data="back_to_main"
    )
    
    # Располагаем кнопки в один столбец (по одной на строку)
    builder.adjust(1)
    
    return builder.as_markup()

def build_students_for_lesson_keyboard(students: list[Student]) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора ученика при создании занятия.
    """
    builder = InlineKeyboardBuilder()
    
    for student in students:
        button_text = student.student_name or student.first_name
        if student.subject:
            button_text += f" ({student.subject})"
        
        builder.button(
            text=button_text,
            callback_data=f"lesson_select_student_{student.id}"  # ← другой префикс
        )
    
    builder.button(
        text="❌ Отмена",
        callback_data="cancel_action"
    )
    
    builder.adjust(1)
    return builder.as_markup()

def student_detail_menu(student_id: int) -> InlineKeyboardMarkup:
    """Меню для управления конкретным учеником"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Здесь позже будут кнопки для управления учеником
            # [InlineKeyboardButton(text="📅 Занятия", callback_data=f"student_lessons_{student_id}")],
            # [InlineKeyboardButton(text="💰 Баланс", callback_data=f"student_balance_{student_id}")],
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_tutor_students")],
        ]
    )