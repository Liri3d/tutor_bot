# db/relp_crud.py
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Relationship, Student, Tutor
from db.base_crud import BaseCRUD


class RelationshipCRUD(BaseCRUD[Relationship]):
    """CRUD для связей"""

    def __init__(self):
        super().__init__(Relationship)

    async def create(
        self,
        session: AsyncSession,
        tutor_id: int,
        student_id: int,
        status: str = "active"
    ) -> Relationship:
        relationship = Relationship(
            tutor_id=tutor_id,
            student_id=student_id,
            status=status
        )
        session.add(relationship)
        await session.commit()
        await session.refresh(relationship)
        return relationship

    async def get_by_tutor_and_student(
        self,
        session: AsyncSession,
        tutor_id: int,
        student_id: int
    ) -> Optional[Relationship]:
        stmt = select(Relationship).where(
            and_(
                Relationship.tutor_id == tutor_id,
                Relationship.student_id == student_id
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_students_for_tutor(
        self,
        session: AsyncSession,
        tutor_id: int
    ) -> List[Student]:
        stmt = select(Student).join(
            Relationship,
            Relationship.student_id == Student.id
        ).where(
            and_(
                Relationship.tutor_id == tutor_id,
                Relationship.status == "active"
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()


relp_crud = RelationshipCRUD()