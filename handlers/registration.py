from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import (
    get_user_by_telegram_id,
    create_user,
    get_invite_by_code,
    get_relationship,
    create_relationship
)
from db.models import User, Relationship


async def register_tutor(
    session: AsyncSession,
    telegram_id: int,
    username: str,
    first_name: str
) -> User:
    """Регистрация репетитора"""
    user = await create_user(
        session=session,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        role='tutor'
    )
    return user


async def register_student_by_invite(
    session: AsyncSession,
    telegram_id: int,
    username: str,
    first_name: str,
    invite_code: str
) -> tuple[User, Relationship]:
    """Регистрация ученика по приглашению"""
    # Проверяем invite
    invite = await get_invite_by_code(session, invite_code)
    if not invite:
        raise ValueError("Недействительное приглашение")
    
    # Проверяем, не пытается ли репетитор подключиться к себе
    tutor = await get_user_by_telegram_id(session, invite.tutor_id)
    if tutor.telegram_id == telegram_id:
        raise ValueError("Нельзя подключиться к самому себе")
    
    # Проверяем существующую связь
    relationship = await get_relationship(session, invite.tutor_id, telegram_id)
    if relationship:
        if relationship.status == 'active':
            raise ValueError("Уже подключены к этому репетитору")
        elif relationship.status == 'inactive':
            # Восстанавливаем связь
            relationship.status = 'active'
            return tutor, relationship
    
    # Создаём ученика
    student = await create_user(
        session=session,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        role='student'
    )
    
    # Создаём связь
    relationship = await create_relationship(
        session=session,
        tutor_id=invite.tutor_id,
        student_id=student.id
    )
    
    # Помечаем invite как использованный
    invite.is_used = True
    
    return tutor, relationship