# services/message_service.py

from typing import Tuple, Optional, List
from aiogram.types import InlineKeyboardMarkup
from db.models import User, Invite
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
            )
        
    @staticmethod
    async def get_change_role_success_message(
        user: User
    ) -> Tuple[str, Optional[InlineKeyboardMarkup], Optional[str]]:
        """
        Получить сообщение об успешной смене роли.
        
        Args:
            user: Объект пользователя
            next_state: Следующее состояние (если нужно)
        
        Returns:
            tuple: (текст сообщения, клавиатура, следующее состояние)
        """
        if user.role == "tutor":
            text = f"✅ Вы сменили роль на репетитора!\n\nВыберите действие:"
            keyboard = tutor_main_menu()
            next_state = "waiting_for_invite"
        else:
            text = f"✅ Вы сменили роль на ученика!\n\nТеперь перейдите по инвайт-ссылке от вашего репетитора:"
            keyboard = None
            next_state = "waiting_for_invite"
        
        return text, keyboard, next_state
        
    @staticmethod
    async def get_change_role_confirm_message(
        user: User       
    ) -> str:
        new_role = "ученика" if user.role == "tutor" else "репетитора"

        return (
            f"⚠️ Вы уверены, что хотите сменить роль на {new_role}?\n\n"
            f"При смене роли вы потеряете доступ к данным, связанным со старой ролью."
        )  

    @staticmethod
    async def get_connect_success_message(
        tutor: User,
    ) -> str:
        if tutor:
            return (
                f"✅ Вы успешно подключились к репетитору!\n"
                f"👤 {tutor.first_name or 'Репетитор'}\n\n"
                "Теперь вы можете просматривать свои занятия и баланс."
            )
    
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
        
        # Получаем сообщение
        message = errors.get(error_type, errors["unknown_error"])
        
        # Подставляем параметры
        if item is not None:
            message = message.replace("{item}", item)
        
        # Подставляем дополнительные параметры
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
        # Основная информация
        text = (
            f"✅ **Приглашение создано!**\n\n"
            f"👤 Ученик: {invite.student_name}\n"
            f"🔑 Код: `{invite.code}`\n"
            f"📅 Действительно до: {invite.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )
        
        # Ссылка для приглашения
        text += (
            f"Отправьте ученику эту ссылку:\n"
            f"`https://t.me/{bot_username}?start=invite_{invite.code}`"
        )
        
        # Дополнительная информация
        if include_usage_info:
            text += (
                f"\n\nℹ️ **Информация:**\n"
                f"• Ссылка действительна до {invite.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"• После использования ссылка становится недействительной\n"
            )
        
        return text

    @staticmethod
    async def get_settings_message(user: User) -> Tuple[str, InlineKeyboardMarkup]:
        """
        Получить сообщение и клавиатуру для меню настроек.
        
        Args:
            user: Объект пользователя
        
        Returns:
            tuple: (текст сообщения, клавиатура)
        """
        text = (
            f"⚙️ **Настройки**\n\n"
            f"👤 Ваша роль: **{user.role}**\n"
            f"📅 Зарегистрирован: {user.registered_at.strftime('%d.%m.%Y')}\n\n"
            f"Здесь вы можете изменить свои настройки."
        )
        
        return text
    




    @staticmethod
    async def format_student_list(
        students: List[User],
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
            # Имя
            name = student.first_name or "Без имени"
            text += f"{idx}. {name}"
            
            # Username
            if show_username and student.username:
                text += f" (@{student.username})"
            
            # Дата регистрации
            if show_registered:
                text += f"\n   📅 Зарегистрирован: {student.registered_at.strftime('%d.%m.%Y')}"
            
            text += "\n"
        
        return text

    @staticmethod
    async def format_student_detail(
        student: User,
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
        
        # Основная информация
        text += f"👤 Имя: {student.first_name or 'Не указано'}\n"
        
        if student.username:
            text += f"🔗 Username: @{student.username}\n"
        else:
            text += "🔗 Username: Нет\n"
        
        text += f"📅 Зарегистрирован: {student.registered_at.strftime('%d.%m.%Y %H:%M')}\n"
        
        # Дополнительная информация
        if show_telegram_id:
            text += f"🆔 Telegram ID: {student.telegram_id}\n"
        
        # Роль
        role_display = "👨‍🏫 Репетитор" if student.role == "tutor" else "👨‍🎓 Ученик"
        text += f"📌 Роль: {role_display}\n"
        
        if show_settings and hasattr(student, 'settings') and student.settings:
            text += f"\n⚙️ **Настройки:**\n"
            for key, value in student.settings.items():
                text += f"• {key}: {value}\n"
        
        # Заглушка для будущих функций
        text += "\n📌 Здесь будут занятия и управление учеником."
        
        return text
    




    @staticmethod
    async def get_main_mune_message(
        user: User,
    ) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
       
        if user.role == "tutor":
            text = "👋 Главное меню репетитора:"
            keyboard = tutor_main_menu()
        else:
            text = "👋 Главное меню ученика:"
            keyboard = student_main_menu()

        return text, keyboard