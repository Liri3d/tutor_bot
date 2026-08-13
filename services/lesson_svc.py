from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from db import Lesson, lesson_crud 


class LessonService:
    """Сервис для работы с занятиями"""

    @staticmethod
    async def get_tutor_lessons(
        session: AsyncSession,
        tutor_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Lesson]:
        """
        Получить занятия репетитора.
        """
        return await lesson_crud.get_tutor_lessons(
            session=session,
            tutor_id=tutor_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            limit=limit
        )