# services/user_service.py

import hashlib
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


class UserService:
    """Сервис для работы с пользователями"""

    # @staticmethod
    # async def create_user(
    #     session: AsyncSession,
    #     telegram_id: int,
    #     role: str,
    #     username: Optional[str] = None,
    #     first_name: Optional[str] = None
    # ) -> User:
    #     """
    #     Создать нового пользователя.
        
    #     Args:
    #         session: Сессия БД
    #         telegram_id: Telegram ID пользователя
    #         role: Роль ('tutor' или 'student')
    #         username: Username из Telegram (опционально)
    #         first_name: Имя из Telegram (опционально)
        
    #     Returns:
    #         User: Созданный пользователь
        
    #     Raises:
    #         ValueError: Если пользователь с таким telegram_id уже существует
    #     """
    #     # Проверяем, не существует ли уже пользователь
    #     existing_user = await db_get_user_by_telegram_id(session, telegram_id)
    #     if existing_user:
    #         raise ValueError(f"Пользователь с Telegram ID {telegram_id} уже существует")
        
    #     # Создаём пользователя через CRUD
    #     user = await db_create_user(
    #         session=session,
    #         telegram_id=telegram_id,
    #         username=username,
    #         first_name=first_name,
    #         role=role
    #     )
        
    #     return user

    # @staticmethod
    # async def create_user_with_password(
    #     session: AsyncSession,
    #     login: str,
    #     password: str,
    #     first_name: str,
    #     role: str = "tutor"
    # ) -> User:
    #     """Создать пользователя с паролем"""
    #     # Хэшируем пароль
    #     salt = secrets.token_hex(16)
    #     hash_obj = hashlib.sha256((salt + password).encode()).hexdigest()
    #     password_hash = f"{salt}:{hash_obj}"
        
    #     user = User(
    #         login=login,
    #         password_hash=password_hash,
    #         first_name=first_name,
    #         role=role
    #     )
    #     session.add(user)
    #     await session.commit()
    #     await session.refresh(user)
    #     return user
    
    # @staticmethod
    # async def get_user_by_id(
    #     session: AsyncSession,
    #     user_id: int
    # ) -> Optional[User]:
    #     """Получить пользователя по ID"""
    #     return await get_user_by_id(session, user_id)

    @staticmethod
    async def get_user_by_telegram_id(
        session: AsyncSession,
        telegram_id: int
    ) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        return await db_get_user_by_telegram_id(session, telegram_id)

    @staticmethod
    async def get_user_by_login(
        session: AsyncSession,
        login: str
    ) -> Optional[User]:
        """Получить пользователя по логину"""
        return await db_get_user_by_login(session, login)
    
    @staticmethod
    async def is_tutor(
        session: AsyncSession,
        telegram_id: int
    ) -> bool:
        """
        Проверить, является ли пользователь репетитором.
        
        Args:
            session: Сессия БД
            telegram_id: Telegram ID пользователя
        
        Returns:
            bool: True, если пользователь репетитор
        """
        user = await db_get_user_by_telegram_id(session, telegram_id)
        return user is not None and user.role == "tutor"

    @staticmethod
    async def is_student(
        session: AsyncSession,
        telegram_id: int
    ) -> bool:
        """
        Проверить, является ли пользователь учеником.
        
        Args:
            session: Сессия БД
            telegram_id: Telegram ID пользователя
        
        Returns:
            bool: True, если пользователь ученик
        """
        user = await db_get_user_by_telegram_id(session, telegram_id)
        return user is not None and user.role == "student"
    
    @staticmethod
    async def change_role(
        session: AsyncSession,
        user: User
    ) -> User:
        """
        Сменить роль пользователя на противоположную.
        
        Args:
            session: Сессия БД
            user: Объект пользователя (должен быть получен из этой же сессии)
        
        Returns:
            User: Обновлённый пользователь
        
        Raises:
            ValueError: Если пользователь не найден или роль некорректна
        """
        # Проверяем, что пользователь существует
        if not user:
            raise ValueError("USER_NOT_FOUND")
        
        # Проверяем, что роль корректна
        if user.role not in ["tutor", "student"]:
            raise ValueError("INVALID_ROLE")
        
        # Меняем роль на противоположную
        new_role = "tutor" if user.role == "student" else "student"
        
        user.role = new_role
        
        # Сохраняем изменения
        await session.commit()
        await session.refresh(user)
        
        return user