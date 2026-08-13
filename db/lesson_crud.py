from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Lesson
from db.base_crud import BaseCRUD


class LessonCRUD(BaseCRUD[Lesson]):
    """CRUD для занятий"""

    def __init__(self):
        super().__init__(Lesson)

    async def create(
        self,
        session: AsyncSession,
        tutor_id: int,
        student_id: int,
        start_time: datetime,
        duration_minutes: int = 60,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        status: str = "scheduled"
    ) -> Lesson:
        lesson = Lesson(
            tutor_id=tutor_id,
            student_id=student_id,
            start_time=start_time,
            duration_minutes=duration_minutes,
            title=title,
            notes=notes,
            status=status
        )
        session.add(lesson)
        await session.commit()
        await session.refresh(lesson)
        return lesson

    async def delete(
        self,
        session: AsyncSession,
        lesson_id: int
    ) -> bool:
        lesson = await self.get_by_id(session, lesson_id)
        if lesson:
            await session.delete(lesson)
            await session.commit()
            return True
        return False

    async def get_tutor_lessons(
        self,
        session: AsyncSession,
        tutor_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Lesson]:
        """
        Получить занятия репетитора с фильтрацией.
        
        Args:
            session: Сессия БД
            tutor_id: ID репетитора
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
            status: Статус занятия (опционально)
            limit: Максимальное количество занятий
        """
        stmt = select(Lesson).where(Lesson.tutor_id == tutor_id)
        
        if start_date:
            stmt = stmt.where(Lesson.start_time >= start_date)
        if end_date:
            stmt = stmt.where(Lesson.start_time <= end_date)
        if status:
            stmt = stmt.where(Lesson.status == status)
        
        stmt = stmt.order_by(Lesson.start_time).limit(limit)
        result = await session.execute(stmt)

        return result.scalars().all()

lesson_crud = LessonCRUD()