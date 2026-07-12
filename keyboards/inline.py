from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def role_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Репетитор",
                    callback_data="role_tutor"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Ученик",
                    callback_data="role_student"
                )
            ]
        ]
    )
