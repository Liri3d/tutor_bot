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

lesson_crud = LessonCRUD()