# services/relp_svc.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from db.models import Tutor, Student, TutorStudentLink
from db.link_crud import link_crud


class LinkService:
    """Сервис для работы со связями репетитор-ученик"""

    @staticmethod
    async def create_link(
        session: AsyncSession,
        tutor_id: int,
        student_id: int,
        status: str = "active"
    ) -> TutorStudentLink:
        """Создать связь между репетитором и учеником."""
        existing = await link_crud.get_by_tutor_and_student(
            session, tutor_id, student_id
        )
        if existing:
            if existing.status == "active":
                raise ValueError("Связь уже существует")
            else:
                # Восстанавливаем неактивную связь
                return await link_crud.update_status(
                    session, tutor_id, student_id, "active"
                )
        return await link_crud.create(session, tutor_id, student_id, status)

    @staticmethod
    async def get_tutor_students(
        session: AsyncSession,
        tutor_id: int
    ) -> List[Student]:
        """Получить всех учеников репетитора."""
        return await link_crud.get_students_for_tutor(session, tutor_id)

    @staticmethod
    async def get_student_tutors(
        session: AsyncSession,
        student_id: int
    ) -> List[Tutor]:
        """Получить всех репетиторов ученика"""
        return await link_crud.get_tutors_for_student(session, student_id)

    @staticmethod
    async def get_relationship(
        session: AsyncSession,
        tutor_id: int,
        student_id: int
    ) -> Optional[TutorStudentLink]:
        """Получить связь между репетитором и учеником"""
        return await link_crud.get_by_tutor_and_student(session, tutor_id, student_id)

    @staticmethod
    async def update_relationship_status(
        session: AsyncSession,
        tutor_id: int,
        student_id: int,
        status: str
    ) -> Optional[TutorStudentLink]:
        """Обновить статус связи"""
        return await link_crud.update_status(session, tutor_id, student_id, status)

    @staticmethod
    async def delete_relationship(
        session: AsyncSession,
        tutor_id: int,
        student_id: int
    ) -> bool:
        """Удалить связь между репетитором и учеником"""
        return await link_crud.delete(session, tutor_id, student_id)