from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def get_guest_keyboard():
    """Клавиатура для незарегистрированного пользователя"""
    buttons = [
        [KeyboardButton(text="📝 Зарегистрироваться")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_tutor_keyboard():
    buttons = [
        [KeyboardButton(text="📅 Мои занятия"), KeyboardButton(text="➕ Добавить занятие")],
        [KeyboardButton(text="👥 Мои ученики"), KeyboardButton(text="🔗 Пригласить ученика")],
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🗑️ Удалить аккаунт")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_student_keyboard():
    """Клавиатура для ученика"""
    buttons = [
        [KeyboardButton(text="📅 Мои занятия"), KeyboardButton(text="💰 Мой баланс")],
        [KeyboardButton(text="👤 Мой репетитор")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def remove_keyboard():
    """Убрать клавиатуру"""
    return ReplyKeyboardRemove()