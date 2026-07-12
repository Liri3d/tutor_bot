from typing import Optional, Tuple
from datetime import datetime, timedelta
import secrets
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Invite, Relationship


# ============ USER ============

async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int
) -> Optional[User]:
    """Получить пользователя по Telegram ID"""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(
    session: AsyncSession,
    user_id: int
) -> Optional[User]:
    """Получить пользователя по ID"""
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    role: str,
    username: Optional[str] = None,
    first_name: Optional[str] = None
) -> User:
    """Создать нового пользователя"""
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        role=role
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# ============ INVITE ============

async def create_invite(
    session: AsyncSession,
    tutor_id: int,
    student_name: str,
    expires_in_days: int = 7
) -> Invite:
    """Создать новое приглашение"""
    # Генерируем уникальный код
    code = secrets.token_urlsafe(8)[:12]
    
    invite = Invite(
        code=code,
        tutor_id=tutor_id,
        student_name=student_name,
        expires_at=datetime.now() + timedelta(days=expires_in_days)
    )
    session.add(invite)
    await session.commit()
    await session.refresh(invite)
    return invite


async def get_invite_by_code(
    session: AsyncSession,
    code: str
) -> Optional[Invite]:
    """Получить приглашение по коду"""
    stmt = select(Invite).where(
        and_(
            Invite.code == code,
            Invite.is_used == False,
            Invite.expires_at > datetime.now()
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def mark_invite_as_used(
    session: AsyncSession,
    invite: Invite
) -> None:
    """Отметить приглашение как использованное"""
    invite.is_used = True
    invite.used_at = datetime.now()
    await session.commit()


# ============ RELATIONSHIP ============

async def get_relationship(
    session: AsyncSession,
    tutor_id: int,
    student_id: int
) -> Optional[Relationship]:
    """Получить связь между репетитором и учеником"""
    stmt = select(Relationship).where(
        and_(
            Relationship.tutor_id == tutor_id,
            Relationship.student_id == student_id
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_relationship(
    session: AsyncSession,
    tutor_id: int,
    student_id: int
) -> Relationship:
    """Создать связь между репетитором и учеником"""
    relationship = Relationship(
        tutor_id=tutor_id,
        student_id=student_id
    )
    session.add(relationship)
    await session.commit()
    await session.refresh(relationship)
    return relationship


async def get_active_relationships_for_tutor(
    session: AsyncSession,
    tutor_id: int
) -> list[Relationship]:
    """Получить все активные связи репетитора"""
    stmt = select(Relationship).where(
        and_(
            Relationship.tutor_id == tutor_id,
            Relationship.status == "active"
        )
    )
    result = await session.execute(stmt)
    return result.scalars().all()