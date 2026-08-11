# services/message_service.py

from typing import Tuple, Optional, List
from aiogram.types import InlineKeyboardMarkup
from db.models import Tutor, Student, Invite
from keyboards import tutor_menu_keyboard, student_menu_keyboard


class MessageService:
    """Сервис для формирования сообщений и меню"""

    @staticmethod
    async def get_welcome_message(user: Student | Tutor) -> Tuple[str, InlineKeyboardMarkup]:
        """
        Получить приветственное сообщение и меню для пользователя.
        
        Args:
            user: Объект пользователя (Student или Tutor)
        
        Returns:
            tuple: (текст сообщения, клавиатура)
        """
        if hasattr(user, 'login'):  # это Tutor
            text = f"👋 С возвращением, {user.first_name or 'репетитор'}!\n\nВыберите действие:"
            keyboard = tutor_menu_keyboard()
        else:  # это Student
            text = f"👋 С возвращением, {user.first_name or 'ученик'}!\n\nВыберите действие:"
            keyboard = student_menu_keyboard()
        
        return text, keyboard

    @staticmethod
    async def get_registration_success_message(
        user: Student,
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
                f"👋 Добро пожаловать, {user.first_name or 'ученик'}!"
            )
    
    @staticmethod
    async def get_connect_success_message(
        tutor: Tutor,
    ) -> str:
        """Сообщение об успешном подключении к репетитору"""
        if tutor:
            return (
                f"✅ Вы успешно подключились к репетитору!\n"
                f"👤 {tutor.first_name or 'Репетитор'}\n\n"
                "Теперь вы можете просматривать свои занятия и баланс."
            )
        return "❌ Репетитор не найден"
    
    @staticmethod
    async def get_invite_instructions() -> str:
        """
        Получить инструкцию по вводу инвайт-кода.
        
        Returns:
            str: Текст инструкции
        """
        return (
            "👨‍🎓 Чтобы подключиться к репетитору,\n"
            "перейдите по пригласительной ссылке. \n"
            "Ссылку можно получить у вашего репетитора."
        )

    # @staticmethod
    # async def get_start_message() -> str:
    #     """
    #     Получить стартовое сообщение для нового пользователя.
        
    #     Returns:
    #         str: Текст сообщения
    #     """
    #     return "👋 Добро пожаловать в Tutor Bot!\n\nЯ помогу вам управлять расписанием и учениками.\n\nНажмите кнопку '🚀 Старт', чтобы начать:", start_menu_keyboard()
        

    @staticmethod
    async def get_error_message(
        error_type: str,
        item: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Получить сообщение об ошибке.
        
        Args:
            error_type: Тип ошибки
            item: Название элемента (для подстановки в сообщение)
            **kwargs: Дополнительные параметры для подстановки
        
        Returns:
            str: Текст ошибки
        """
        errors = {
            # === ПОЛЬЗОВАТЕЛИ ===
            "user_not_found": "❌ Пользователь не найден.",
            "already_registered": "❌ Вы уже зарегистрированы.",
            "permission_denied": "❌ У вас нет прав на это действие.",
            
            # === РОЛИ ===
            "tutor_as_student": (
                "❌ Вы зарегистрированы как репетитор.\n\n"
                "Чтобы подключиться к другому репетитору как ученик, смените свою роль в настройках:\n"
                "Настройки → Сменить роль на ученика"
            ),
            "student_as_tutor": "❌ Ученик не может выполнять это действие.",
            "role_change_impossible": "❌ Невозможно сменить роль. Обратитесь к администратору.",
            "role_change_same": "❌ Вы уже являетесь этой ролью.",
            
            # === ПРИГЛАШЕНИЯ ===
            "invalid_invite": (
                "❌ Недействительный код приглашения.\n\n"
                "Код мог быть неверным, использованным или истекшим.\n"
                "Пожалуйста, проверьте код и попробуйте снова."
            ),
            "self_invite": "❌ Нельзя подключиться к самому себе!",
            "already_connected": "✅ Вы уже подключены к этому репетитору!",
            "invite_expired": "❌ Срок действия приглашения истёк.",
            "invite_used": "❌ Это приглашение уже было использовано.",
            
            # === УЧЕНИКИ ===
            "student_not_found": "❌ Ученик не найден.",
            "no_students": "👤 У вас пока нет учеников.\n\nСоздайте приглашение, чтобы добавить ученика.",
            
            # === ВАЛИДАЦИЯ ===
            "invalid_name": "❌ Имя должно содержать хотя бы 2 символа. Попробуйте снова:",
            "invalid_date": "❌ Некорректная дата. Используйте формат ДД.ММ.ГГГГ.",
            "invalid_time": "❌ Некорректное время. Используйте формат ЧЧ:ММ.",
            "invalid_duration": "❌ Длительность должна быть от 10 до 180 минут.",
            "past_date": "❌ Нельзя создавать занятие в прошлом.",
            "past_time": "❌ Нельзя создать занятие раньше текущего времени.",
            "overlap": "❌ Время пересекается с уже запланированным занятием.",
            "out_of_day": "❌ Занятие выходит за пределы дня. Укажите более раннее время или меньшую длительность.",
            
            # === ДРУГОЕ ===
            "unknown_error": "❌ Произошла неизвестная ошибка. Попробуйте позже.",
            "not_found": "❌ {item} не найден.",
            "already_exists": "❌ {item} уже существует.",
        }
        
        message = errors.get(error_type, errors["unknown_error"])
        
        if item is not None:
            message = message.replace("{item}", item)
        
        for key, value in kwargs.items():
            if isinstance(value, str):
                message = message.replace(f"{{{key}}}", value)
        
        return message

    @staticmethod
    async def get_invite_prompt() -> str:
        """
        Получить текст для приглашения ученика.
        
        Returns:
            str: Текст приглашения
        """
        return (
            "👤 **Пригласить ученика**\n\n"
            "Введите имя ученика, которого хотите пригласить:"
        )

    @staticmethod
    async def format_invite(
        invite: Invite,
        bot_username: str,
        include_usage_info: bool = True
    ) -> str:
        """
        Сформировать сообщение о созданном приглашении.
        
        Args:
            invite: Объект приглашения
            bot_username: Username бота (для генерации ссылки)
            include_usage_info: Включать ли информацию об использовании
        
        Returns:
            str: Отформатированное сообщение
        """
        text = (
            f"✅ **Приглашение создано!**\n\n"
            f"👤 Ученик: {invite.student_name}\n"
            f"🔑 Код: `{invite.code}`\n"
            f"📅 Действительно до: {invite.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )
        
        text += (
            f"Отправьте ученику эту ссылку:\n"
            f"`https://t.me/{bot_username}?start=invite_{invite.code}`"
        )
        
        if include_usage_info:
            text += (
                f"\n\nℹ️ **Информация:**\n"
                f"• Ссылка действительна до {invite.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"• После использования ссылка становится недействительной\n"
            )
        
        return text

    @staticmethod
    async def get_settings_message(user: Student | Tutor) -> str:
        """
        Получить сообщение для меню настроек.
        
        Args:
            user: Объект пользователя (Student или Tutor)
        
        Returns:
            str: Текст сообщения
        """
        # Определяем роль
        if hasattr(user, 'login'):
            role_display = "репетитор"
            registered_at = user.registered_at if hasattr(user, 'registered_at') else "неизвестно"
        else:
            role_display = "ученик"
            registered_at = user.registered_at if hasattr(user, 'registered_at') else "неизвестно"
        
        return (
            f"⚙️ **Настройки**\n\n"
            f"👤 Ваша роль: **{role_display}**\n"
            f"📅 Зарегистрирован: {registered_at.strftime('%d.%m.%Y') if hasattr(registered_at, 'strftime') else registered_at}\n\n"
            f"Здесь вы можете изменить свои настройки."
        )

    @staticmethod
    async def format_student_list(
        students: List[Student],
        show_username: bool = True,
        show_registered: bool = False
    ) -> str:
        """
        Сформировать список учеников для репетитора.
        
        Args:
            students: Список учеников
            show_username: Показывать ли username
            show_registered: Показывать ли дату регистрации
        
        Returns:
            str: Отформатированный список
        """
        if not students:
            return "👤 У вас пока нет учеников.\n\nСоздайте приглашение, чтобы добавить ученика."
        
        text = f"👤 **Ваши ученики**\n\nВсего: {len(students)}\n\n"
        
        for idx, student in enumerate(students, 1):
            name = student.first_name or "Без имени"
            text += f"{idx}. {name}"
            
            if show_username and student.username:
                text += f" (@{student.username})"
            
            if show_registered and hasattr(student, 'registered_at'):
                text += f"\n   📅 Зарегистрирован: {student.registered_at.strftime('%d.%m.%Y')}"
            
            text += "\n"
        
        return text

    @staticmethod
    async def format_student_detail(
        student: Student,
        show_telegram_id: bool = False,
        show_settings: bool = False
    ) -> str:
        """
        Сформировать детальную информацию об ученике.
        
        Args:
            student: Объект ученика
            show_telegram_id: Показывать ли Telegram ID
            show_settings: Показывать ли настройки
        
        Returns:
            str: Отформатированная информация
        """
        text = "📋 **Информация об ученике**\n\n"
        
        text += f"👤 Имя: {student.first_name or 'Не указано'}\n"
        
        if student.username:
            text += f"🔗 Username: @{student.username}\n"
        else:
            text += "🔗 Username: Нет\n"
        
        if hasattr(student, 'registered_at'):
            text += f"📅 Зарегистрирован: {student.registered_at.strftime('%d.%m.%Y %H:%M')}\n"
        
        if show_telegram_id:
            text += f"🆔 Telegram ID: {student.telegram_id}\n"
        
        # ✅ ИСПРАВЛЕНО: у Student нет role, всегда ученик
        text += "📌 Роль: 👨‍🎓 Ученик\n"
        
        # Заглушка для будущих функций
        text += "\n📌 Здесь будут занятия и управление учеником."
        
        return text

    @staticmethod
    async def get_main_menu_message(
        user: Student | Tutor,
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
        """
        Получить главное меню для пользователя.
        
        Args:
            user: Объект пользователя (Student или Tutor)
        
        Returns:
            tuple: (текст сообщения, клавиатура)
        """
        if hasattr(user, 'login'):  # это Tutor
            text = "👋 Главное меню репетитора:"
            keyboard = tutor_menu_keyboard()
        else:  # это Student
            text = "👋 Главное меню ученика:"
            keyboard = student_menu_keyboard()

        return text, keyboard