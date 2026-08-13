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
        student_name: str,
        telegram_id: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        gender: Optional[str] = None,
        age: Optional[int] = None,
        subject: Optional[str] = None,
    ) -> Student:
        student = Student(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            student_name=student_name,
            gender=gender,
            age=age,
            subject=subject,
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)
        return student


student_crud = StudentCRUD()