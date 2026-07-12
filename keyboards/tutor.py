from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def tutor_main_menu() -> InlineKeyboardMarkup:
    """Главное меню репетитора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # [InlineKeyboardButton(text="📅 Моё расписание", callback_data="tutor_schedule")],
            # [InlineKeyboardButton(text="👥 Мои ученики", callback_data="tutor_students")],
            # [InlineKeyboardButton(text="➕ Добавить занятие", callback_data="tutor_add_lesson")],
            [InlineKeyboardButton(text="🔗 Пригласить ученика", callback_data="tutor_invite")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings_menu")],
        ]
    )