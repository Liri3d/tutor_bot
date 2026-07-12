# services/message_service.py

from typing import Tuple
from aiogram.types import InlineKeyboardMarkup
from db.models import User
from keyboards import tutor_main_menu, student_main_menu


class MessageService:
    """Сервис для формирования сообщений и меню"""

    @staticmethod
    async def get_welcome_message(user: User) -> Tuple[str, InlineKeyboardMarkup]:
        """
        Получить приветственное сообщение и меню для пользователя.
        
        Args:
            user: Объект пользователя
        
        Returns:
            tuple: (текст сообщения, клавиатура)
        """
        if user.role == "tutor":
            text = f"👋 С возвращением, {user.first_name or 'репетитор'}!\n\nВыберите действие:"
            keyboard = tutor_main_menu()
        else:
            text = f"👋 С возвращением, {user.first_name or 'ученик'}!\n\nВыберите действие:"
            keyboard = student_main_menu()
        
        return text, keyboard

    @staticmethod
    async def get_registration_success_message(
        user: User,
        role: str
    ) -> str:
        """
        Получить сообщение об успешной регистрации.
        
        Args:
            user: Объект пользователя
            role: Роль ('tutor' или 'student')
        
        Returns:
            str: Текст сообщения
        """
        if role == "tutor":
            return (
                f"✅ Вы зарегистрированы как репетитор!\n\n"
                f"👋 Добро пожаловать, {user.first_name or 'репетитор'}!"
            )
        else:
            return (
                f"✅ Вы зарегистрированы как ученик!\n\n"
                f"👋 Добро пожаловать, {user.first_name or 'ученик'}!\n\n"
                f"Чтобы подключиться к репетитору, перейдите по пригласительной ссылке."
            )

    # @staticmethod
    # async def get_invite_instructions() -> str:
    #     """
    #     Получить инструкцию по вводу инвайт-кода.
        
    #     Returns:
    #         str: Текст инструкции
    #     """
    #     return (
    #         "👨‍🎓 Чтобы подключиться к репетитору,\n"
    #         "введите код приглашения:\n\n"
    #         "Например: `ABC123`"
    #     )

    @staticmethod
    async def get_start_message() -> str:
        """
        Получить стартовое сообщение для нового пользователя.
        
        Returns:
            str: Текст сообщения
        """
        return (
            "👋 Добро пожаловать в Tutor Bot!\n\n"
            "Я помогу вам управлять своим расписанием.\n\n"
            "Вы ученик или репетитор?"
        )