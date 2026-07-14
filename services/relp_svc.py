from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import *
from db.models import User, Relationship


class RelationshipService:
    """Сервис для работы со связями репетитор-ученик"""

    @staticmethod
    async def get_tutor_students(
        session: AsyncSession,
        tutor_id: int
    ) -> List[User]:
        """
        Получить всех учеников репетитора.
        
        Args:
            session: Сессия БД
            tutor_id: ID репетитора
        
        Returns:
            List[User]: Список учеников
        """
        # Получаем все активные связи
        relationships = await db_get_active_relationships_for_tutor(session, tutor_id)
        
        students = []
        for rel in relationships:
            student = await db_get_user_by_id(session, rel.student_id)
            if student:
                students.append(student)
        
        return students
    


    # @staticmethod
    # async def get_student_by_relationship_id(
    #     session: AsyncSession,
    #     relationship_id: int
    # ) -> Optional[User]:
    #     """Получить ученика по ID связи"""
    #     # Если нужно получить ученика по relationship_id
    #     from db.models import Relationship
    #     relationship = await session.get(Relationship, relationship_id)
    #     if not relationship:
    #         return None
    #     return await get_user_by_id(session, relationship.student_id)

    # @staticmethod
    # async def get_or_create_relationship(
    #     session: AsyncSession,
    #     tutor_id: int,
    #     student_id: int
    # ) -> Relationship:
    #     """
    #     Получить или создать связь между репетитором и учеником.
        
    #     Args:
    #         session: Сессия БД
    #         tutor_id: ID репетитора
    #         student_id: ID ученика
        
    #     Returns:
    #         Relationship: Связь
    #     """
    #     relationship = await get_relationship(session, tutor_id, student_id)
    #     if relationship:
    #         return relationship
        
    #     return await create_relationship(session, tutor_id, student_id)

    # @staticmethod
    # async def get_students_with_details(
    #     session: AsyncSession,
    #     tutor_id: int
    # ) -> List[dict]:
    #     """
    #     Получить учеников с дополнительной информацией.
        
    #     Returns:
    #         List[dict]: [
    #             {
    #                 "user": User,
    #                 "relationship_id": int,
    #                 "joined_at": datetime,
    #             }
    #         ]
    #     """
    #     relationships = await get_active_relationships_for_tutor(session, tutor_id)
        
    #     result = []
    #     for rel in relationships:
    #         student = await get_user_by_id(session, rel.student_id)
    #         if student:
    #             result.append({
    #                 "user": student,
    #                 "relationship_id": rel.id,
    #                 "joined_at": rel.created_at,
    #             })
        
    #     return result