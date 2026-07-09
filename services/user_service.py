"""Сервис для работы с пользователями"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import (
    get_user_by_telegram_id,
    create_user,
    get_tutor_students
)
from db.models import User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    role: str,
    username: Optional[str] = None,
    first_name: Optional[str] = None
) -> User:
    """
    Получить пользователя по telegram_id, или создать нового.
    """
    user = await get_user_by_telegram_id(session, telegram_id)
    if user:
        return user
    
    return await create_user(
        session=session,
        telegram_id=telegram_id,
        role=role,
        username=username,
        first_name=first_name
    )


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    return await session.get(User, user_id)


async def get_user_by_telegram(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Получить пользователя по Telegram ID"""
    return await get_user_by_telegram_id(session, telegram_id)


async def get_tutor_students_list(session: AsyncSession, tutor_id: int):
    """Получить всех учеников репетитора"""
    return await get_tutor_students(session, tutor_id)