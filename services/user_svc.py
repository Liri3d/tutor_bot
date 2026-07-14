# services/user_service.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import *
from db.models import User


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    async def create_user(
        session: AsyncSession,
        telegram_id: int,
        role: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> User:
        """
        Создать нового пользователя.
        
        Args:
            session: Сессия БД
            telegram_id: Telegram ID пользователя
            role: Роль ('tutor' или 'student')
            username: Username из Telegram (опционально)
            first_name: Имя из Telegram (опционально)
        
        Returns:
            User: Созданный пользователь
        
        Raises:
            ValueError: Если пользователь с таким telegram_id уже существует
        """
        # Проверяем, не существует ли уже пользователь
        existing_user = await db_get_user_by_telegram_id(session, telegram_id)
        if existing_user:
            raise ValueError(f"Пользователь с Telegram ID {telegram_id} уже существует")
        
        # Создаём пользователя через CRUD
        user = await db_create_user(
            session=session,
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            role=role
        )
        
        return user

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

    # @staticmethod
    # async def change_role(
    #     session: AsyncSession,
    #     telegram_id: int,
    #     new_role: str
    # ) -> User:
    #     """Сменить роль пользователя"""
    #     user = await get_user_by_telegram_id(session, telegram_id)
    #     if not user:
    #         raise ValueError("Пользователь не найден")
        
    #     if user.role == new_role:
    #         raise ValueError(f"Вы уже являетесь {new_role}")
        
    #     user.role = new_role
    #     await session.commit()
    #     await session.refresh(user)
    #     return user

    # services/user_service.py

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