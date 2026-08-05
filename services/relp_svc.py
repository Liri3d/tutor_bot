# services/relp_svc.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Student, Relationship
from db.relp_crud import relp_crud


class RelationshipService:
    """Сервис для работы со связями репетитор-ученик"""

    @staticmethod
    async def create_relationship(
        session: AsyncSession,
        tutor_id: int,
        student_id: int
    ) -> Relationship:
        """Создать связь между репетитором и учеником."""
        existing = await relp_crud.get_by_tutor_and_student(
            session, tutor_id, student_id
        )
        if existing:
            raise ValueError("Связь уже существует")
        
        return await relp_crud.create(session, tutor_id, student_id)

    @staticmethod
    async def get_tutor_students(
        session: AsyncSession,
        tutor_id: int
    ) -> List[Student]:
        """Получить всех учеников репетитора."""
        return await relp_crud.get_students_for_tutor(session, tutor_id)