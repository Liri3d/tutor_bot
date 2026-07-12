from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def settings_menu(current_role: str) -> InlineKeyboardMarkup:
    """
    Меню настроек.
    current_role: 'tutor' или 'student' — чтобы показать, какая роль активна.
    """
    role_text = "🔄 Сменить роль на Ученик" if current_role == "tutor" else "🔄 Сменить роль на Репетитор"
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=role_text, callback_data="change_role_confirm")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
        ]
    )

def confirm_change_role_menu() -> InlineKeyboardMarkup:
    """Подтверждение смены роли"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, сменить", callback_data="change_role_yes")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="change_role_no")],
        ]
    )

# def change_role_keyboard():
#     return InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [
#                     InlineKeyboardButton(
#                         text=f"🔄 На репетитора" if user.role == "student" else "🔄 На ученика",
#                         callback_data="confirm_change_role"
#                     )
#                 ],
#                 [
#                     InlineKeyboardButton(
#                         text="❌ Отмена",
#                         callback_data="cancel_change_role"
#                     )
#                 ]
#             ]
#         )


