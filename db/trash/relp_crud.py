# from typing import Optional, Tuple
# from datetime import datetime, timedelta
# import secrets
# from sqlalchemy import select, and_
# from sqlalchemy.ext.asyncio import AsyncSession

# from .models import User, Invite, Relationship

# async def db_get_relationship(
#     session: AsyncSession,
#     tutor_id: int,
#     student_id: int
# ) -> Optional[Relationship]:
#     """Получить связь между репетитором и учеником"""
#     stmt = select(Relationship).where(
#         and_(
#             Relationship.tutor_id == tutor_id,
#             Relationship.student_id == student_id
#         )
#     )
#     result = await session.execute(stmt)
#     return result.scalar_one_or_none()


# async def db_create_relationship(
#     session: AsyncSession,
#     tutor_id: int,
#     student_id: int
# ) -> Relationship:
#     """Создать связь между репетитором и учеником"""
#     relationship = Relationship(
#         tutor_id=tutor_id,
#         student_id=student_id
#     )
#     session.add(relationship)
#     await session.commit()
#     await session.refresh(relationship)
#     return relationship


# async def db_get_active_relationships_for_tutor(
#     session: AsyncSession,
#     tutor_id: int
# ) -> list[Relationship]:
#     """Получить все активные связи репетитора"""
#     stmt = select(Relationship).where(
#         and_(
#             Relationship.tutor_id == tutor_id,
#             Relationship.status == "active"
#         )
#     )
#     result = await session.execute(stmt)
#     return result.scalars().all()