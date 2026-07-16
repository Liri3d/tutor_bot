from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Student
from db.base_crud import BaseCRUD


class StudentCRUD(BaseCRUD[Student]):
    """CRUD для учеников"""

    def __init__(self):
        super().__init__(Student)

    async def get_by_telegram_id(self, session: AsyncSession, telegram_id: int) -> Optional[Student]:
        stmt = select(Student).where(Student.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Student:
        student = Student(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
            phone=phone,
            role="student"
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)
        return student


student_crud = StudentCRUD()