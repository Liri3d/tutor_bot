# services/session_service.py

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db import *


class SessionService:
    """
    Сервис для управления сессиями базы данных.
    Предоставляет единую точку доступа к сессиям для всех сервисов и хендлеров.
    """

    @staticmethod
    async def init_db() -> None:
        """
        Инициализация базы данных — создание всех таблиц.
        
        Returns:
            None
        
        Example:
            # В main.py
            await SessionService.init_db()
        """
        await db_init_db()

    @staticmethod
    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        """
        Получить сессию базы данных.
        
        Returns:
            AsyncGenerator[AsyncSession, None]: Генератор сессий
        
        Yields:
            AsyncSession: Сессия базы данных
        
        Example:
            async for session in SessionService.get_session():
                user = await UserService.get_user_by_telegram_id(session, telegram_id)
        """
        async for session in db_get_session():
            yield session