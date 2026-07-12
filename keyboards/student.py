from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def student_main_menu() -> InlineKeyboardMarkup:
    """Главное меню ученика"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # [InlineKeyboardButton(text="📅 Мои занятия", callback_data="student_lessons")],
            # [InlineKeyboardButton(text="💰 Мой баланс", callback_data="student_balance")],
            # [InlineKeyboardButton(text="👤 Мой репетитор", callback_data="student_tutor")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings_menu")],
        ]
    )