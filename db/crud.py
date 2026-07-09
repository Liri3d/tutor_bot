from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import User, Invite, Relationship, Subscription, Lesson


# ============ USER CRUD ============

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Получить пользователя по Telegram ID"""
    stmt = select(User).where(User.telegram_id == telegram_id)
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
    await session.flush()
    return user


async def get_tutor_students(session: AsyncSession, tutor_id: int) -> List[User]:
    """Получить всех активных учеников репетитора"""
    stmt = (
        select(User)
        .join(Relationship, Relationship.student_id == User.id)
        .where(
            and_(
                Relationship.tutor_id == tutor_id,
                Relationship.status == 'active'
            )
        )
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ============ INVITE CRUD ============

async def get_invite_by_code(session: AsyncSession, code: str) -> Optional[Invite]:
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


async def create_invite(
    session: AsyncSession,
    tutor_id: int,
    expires_at: datetime
) -> Invite:
    """Создать новое приглашение"""
    import secrets
    code = secrets.token_urlsafe(8)[:12]  # Генерируем короткий код
    
    invite = Invite(
        code=code,
        tutor_id=tutor_id,
        expires_at=expires_at
    )
    session.add(invite)
    await session.flush()
    return invite


# ============ RELATIONSHIP CRUD ============

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
    """Создать связь репетитор-ученик"""
    relationship = Relationship(
        tutor_id=tutor_id,
        student_id=student_id,
        status='active'
    )
    session.add(relationship)
    await session.flush()
    return relationship


# ============ LESSON CRUD ============

async def get_lessons_for_student(
    session: AsyncSession,
    student_id: int,
    limit: int = 10
) -> List[Lesson]:
    """Получить занятия ученика"""
    stmt = (
        select(Lesson)
        .join(Relationship, Lesson.relationship_id == Relationship.id)
        .where(
            and_(
                Relationship.student_id == student_id,
                Lesson.status == 'scheduled'
            )
        )
        .order_by(Lesson.start_time)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_lesson(
    session: AsyncSession,
    relationship_id: int,
    start_time: datetime,
    duration_minutes: int,
    subject: Optional[str] = None,
    paid: bool = True
) -> Lesson:
    """Создать новое занятие"""
    lesson = Lesson(
        relationship_id=relationship_id,
        start_time=start_time,
        duration_minutes=duration_minutes,
        subject=subject,
        paid=paid
    )
    session.add(lesson)
    await session.flush()
    return lesson

async def delete_user_cascade(session: AsyncSession, user_id: int) -> None:
    """
    Каскадное удаление пользователя и всех связанных записей.
    """
    from sqlalchemy import delete, and_, not_
    from .models import User, Invite, Relationship, Subscription, Lesson
    
    # 1. Находим учеников, которые связаны ТОЛЬКО с этим репетитором
    #    (чтобы не удалять учеников у других репетиторов)
    stmt = (
        select(Relationship.student_id)
        .where(Relationship.tutor_id == user_id)
        .group_by(Relationship.student_id)
        .having(func.count(Relationship.tutor_id) == 1)
    )
    result = await session.execute(stmt)
    orphan_student_ids = [row[0] for row in result.all()]
    
    # 2. Удаляем орфан-учеников (связанных только с этим репетитором)
    if orphan_student_ids:
        await session.execute(
            delete(User).where(User.id.in_(orphan_student_ids))
        )
    
    # 3. Удаляем все связи репетитора
    await session.execute(
        delete(Relationship).where(
            or_(
                Relationship.tutor_id == user_id,
                Relationship.student_id == user_id
            )
        )
    )
    
    # 4. Удаляем все приглашения репетитора
    await session.execute(
        delete(Invite).where(Invite.tutor_id == user_id)
    )
    
    # 5. Удаляем занятия и абонементы — они удалятся каскадно,
    #    но для уверенности можно удалить явно
    
    # 6. Удаляем самого пользователя
    await session.execute(
        delete(User).where(User.id == user_id)
    )