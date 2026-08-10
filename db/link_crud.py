# db/relp_crud.py
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db.models import Student, Tutor, TutorStudentLink
from db.base_crud import BaseCRUD


class LinkCRUD(BaseCRUD[TutorStudentLink]):
    """CRUD для связей"""

    def __init__(self):
        super().__init__(TutorStudentLink)

    async def create(
        self,
        session: AsyncSession,
        tutor_id: int,
        student_id: int,
        status: str = "active"
    ) -> TutorStudentLink:
        link = TutorStudentLink(
            tutor_id=tutor_id,
            student_id=student_id,
            status=status
        )
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link

    async def get_by_tutor_and_student(
        self,
        session: AsyncSession,
        tutor_id: int,
        student_id: int
    ) -> Optional[TutorStudentLink]:
        """Получить связь по ID репетитора и ученика"""
        stmt = select(TutorStudentLink).where(
            and_(
                TutorStudentLink.tutor_id == tutor_id,
                TutorStudentLink.student_id == student_id
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_students_for_tutor(
        self,
        session: AsyncSession,
        tutor_id: int
    ) -> List[Student]:
        """Получить всех учеников для репетитора"""
        stmt = select(Student).join(
            TutorStudentLink,
            TutorStudentLink.student_id == Student.id
        ).where(TutorStudentLink.tutor_id == tutor_id)
        
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_tutors_for_student(
        self,
        session: AsyncSession,
        student_id: int
    ) -> List[Tutor]:
        """Получить всех репетиторов для ученика"""
        stmt = select(Tutor).join(
            TutorStudentLink,
            TutorStudentLink.tutor_id == Tutor.id
        ).where(TutorStudentLink.student_id == student_id)
        
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self,
        session: AsyncSession,
        tutor_id: int,
        student_id: int,
        status: str
    ) -> Optional[TutorStudentLink]:
        """Обновить статус связи"""
        link = await self.get_by_tutor_and_student(session, tutor_id, student_id)
        if link:
            link.status = status
            link.updated_at = datetime.now()
            await session.commit()
            await session.refresh(link)
        return link

    async def delete(
        self,
        session: AsyncSession,
        tutor_id: int,
        student_id: int
    ) -> bool:
        """Удалить связь между репетитором и учеником"""
        link = await self.get_by_tutor_and_student(session, tutor_id, student_id)
        if link:
            await session.delete(link)
            await session.commit()
            return True
        return False


link_crud = LinkCRUD()