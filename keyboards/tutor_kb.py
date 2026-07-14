from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def tutor_main_menu() -> InlineKeyboardMarkup:
    """Главное меню репетитора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # [InlineKeyboardButton(text="📅 Моё расписание", callback_data="tutor_schedule")],
            [InlineKeyboardButton(text="👥 Мои ученики", callback_data="tutor_students")],
            # [InlineKeyboardButton(text="➕ Добавить занятие", callback_data="tutor_add_lesson")],
            [InlineKeyboardButton(text="🔗 Пригласить ученика", callback_data="tutor_invite")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings_menu")],
        ]
    )

def build_students_keyboard(students: list, tutor_id: int) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру со списком учеников.
    Каждая кнопка — это ученик, callback_data содержит его ID.
    """
    builder = InlineKeyboardBuilder()
    
    for student in students:
        # Формируем текст кнопки: имя + username (если есть)
        button_text = student.first_name or "Без имени"
        if student.username:
            button_text += f" (@{student.username})"
        
        # Добавляем кнопку с callback_data, содержащим ID ученика
        builder.button(
            text=button_text,
            callback_data=f"student_{student.id}"  # Уникальный идентификатор
        )
    
    # Добавляем кнопку "Назад" в меню репетитора
    builder.button(
        text="🔙 Назад",
        callback_data="back_to_main"
    )
    
    # Располагаем кнопки в один столбец (по одной на строку)
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