"""Сервис для работы со связями репетитор-ученик"""

from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.crud import (
    get_relationship,
    create_relationship,
    get_invite_by_code,
    get_user_by_telegram_id,
    create_user
)
from db.models import User, Relationship, Invite


async def get_or_create_relationship(
    session: AsyncSession,
    tutor_id: int,
    student_id: int
) -> Tuple[Relationship, bool]:
    """
    Получить существующую связь или создать новую.
    Возвращает (relationship, created) где created — bool.
    """
    rel = await get_relationship(session, tutor_id, student_id)
    if rel:
        if rel.status == 'inactive':
            rel.status = 'active'
            rel.updated_at = datetime.now()
            return rel, False
        return rel, False
    
    rel = await create_relationship(session, tutor_id, student_id)
    return rel, True


async def register_student_by_invite(
    session: AsyncSession,
    telegram_id: int,
    invite_code: str,
    username: Optional[str] = None,
    first_name: Optional[str] = None
) -> Tuple[User, Relationship]:
    """
    Регистрация ученика по приглашению.
    Возвращает (tutor, relationship)
    """
    # Проверяем приглашение
    invite = await get_invite_by_code(session, invite_code)
    if not invite:
        raise ValueError("Недействительное приглашение")
    
    # Проверяем, что репетитор не пытается подключиться к себе
    tutor = await get_user_by_telegram_id(session, invite.tutor_id)
    if tutor.telegram_id == telegram_id:
        raise ValueError("Нельзя подключиться к самому себе")
    
    # Проверяем существующую связь
    existing_rel = await get_relationship(session, invite.tutor_id, telegram_id)
    if existing_rel and existing_rel.status == 'active':
        raise ValueError("Уже подключены к этому репетитору")
    
    # Создаём или получаем ученика
    student = await get_user_by_telegram_id(session, telegram_id)
    if not student:
        student = await create_user(
            session=session,
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            role='student'
        )
    
    # Создаём или восстанавливаем связь
    if existing_rel and existing_rel.status == 'inactive':
        existing_rel.status = 'active'
        existing_rel.updated_at = datetime.now()
        relationship = existing_rel
    else:
        relationship = await create_relationship(
            session=session,
            tutor_id=invite.tutor_id,
            student_id=student.id
        )
    
    # Помечаем приглашение как использованное
    invite.is_used = True
    
    return tutor, relationship


async def detach_student(
    session: AsyncSession,
    tutor_id: int,
    student_id: int
) -> bool:
    """
    Отвязать ученика от репетитора.
    Отменяет все будущие занятия.
    """
    rel = await get_relationship(session, tutor_id, student_id)
    if not rel or rel.status != 'active':
        raise ValueError("Активная связь с учеником не найдена")
    
    rel.status = 'inactive'
    rel.updated_at = datetime.now()
    
    # Отменяем все будущие занятия
    from db.models import Lesson
    stmt = select(Lesson).where(
        and_(
            Lesson.relationship_id == rel.id,
            Lesson.status == 'scheduled',
            Lesson.start_time > datetime.now()
        )
    )
    result = await session.execute(stmt)
    lessons = result.scalars().all()
    
    for lesson in lessons:
        lesson.status = 'cancelled'
    
    return True


async def create_invite_code(
    session: AsyncSession,
    tutor_id: int,
    expires_days: int = 7
) -> str:
    """Создать новый инвайт-код"""
    from datetime import datetime, timedelta
    from db.crud import create_invite
    
    expires_at = datetime.now() + timedelta(days=expires_days)
    invite = await create_invite(session, tutor_id, expires_at)
    return invite.code