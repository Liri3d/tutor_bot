from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def start_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для неавторизованного пользователя - только кнопка Старт"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Старт")]
        ],
        resize_keyboard=True,  # Автоматический размер
        one_time_keyboard=False  # Клавиатура остаётся после нажатия
    )

def role_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Репетитор",
                    callback_data="role_tutor"
                )
            ],
            # [
            #     InlineKeyboardButton(
            #         text="Ученик",
            #         callback_data="role_student"
            #     )
            # ]
        ]
    )

def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
        ]
    )