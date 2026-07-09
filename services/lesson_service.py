"""Сервис для работы с занятиями"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.crud import create_lesson, get_lessons_for_student
from db.models import Lesson, Relationship


async def create_new_lesson(
    session: AsyncSession,
    relationship_id: int,
    start_time: datetime,
    duration_minutes: int,
    subject: Optional[str] = None,
    paid: bool = True,
) -> Lesson:
    """Создать новое занятие"""
    # Проверяем пересечения с другими занятиями
    stmt = select(Lesson).where(
        and_(
            Lesson.relationship_id == relationship_id,
            Lesson.status == "scheduled",
            Lesson.start_time < start_time + timedelta(minutes=duration_minutes),
            Lesson.start_time + timedelta(minutes=Lesson.duration_minutes) > start_time,
        )
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("Время пересекается с уже запланированным занятием")

    return await create_lesson(
        session=session,
        relationship_id=relationship_id,
        start_time=start_time,
        duration_minutes=duration_minutes,
        subject=subject,
        paid=paid,
    )


async def get_student_lessons(
    session: AsyncSession,
    student_id: int,
    limit: int = 10,
) -> List[Lesson]:
    """Получить предстоящие занятия ученика"""
    return await get_lessons_for_student(session, student_id, limit)


async def cancel_lesson(
    session: AsyncSession,
    lesson_id: int,
    student_id: int,
    free_cancellation_hours: int = 3,
) -> bool:
    """
    Отменить занятие учеником.
    Возвращает True если отмена бесплатная, False если со списанием.
    """
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise ValueError("Занятие не найдено")

    # Проверяем, что занятие принадлежит этому ученику
    relationship = await session.get(Relationship, lesson.relationship_id)
    if not relationship or relationship.student_id != student_id:
        raise ValueError("Это не ваше занятие")

    if lesson.status != "scheduled":
        raise ValueError("Занятие уже нельзя отменить")

    time_until = lesson.start_time - datetime.now()
    hours_until = time_until.total_seconds() / 3600

    lesson.status = "cancelled"

    # Если отмена менее чем за free_cancellation_hours — списываем занятие
    if hours_until < free_cancellation_hours:
        # Здесь будет логика списания из абонемента
        # Пока просто возвращаем False
        return False

    return True

