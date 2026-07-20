# from typing import Optional, Tuple
# from datetime import datetime, timedelta
# import secrets
# from sqlalchemy import select, and_
# from sqlalchemy.ext.asyncio import AsyncSession

# from ..models import User, Invite, Relationship

# async def db_create_invite(
#     session: AsyncSession,
#     tutor_id: int,
#     student_name: str,
#     expires_in_days: int = 7
# ) -> Invite:
#     """Создать новое приглашение"""
#     # Генерируем уникальный код
#     code = secrets.token_urlsafe(8)[:12]
    
#     invite = Invite(
#         code=code,
#         tutor_id=tutor_id,
#         student_name=student_name,
#         expires_at=datetime.now() + timedelta(days=expires_in_days)
#     )
#     session.add(invite)
#     await session.commit()
#     await session.refresh(invite)
#     return invite


# async def db_get_invite_by_code(
#     session: AsyncSession,
#     code: str
# ) -> Optional[Invite]:
#     """Получить приглашение по коду"""
#     stmt = select(Invite).where(
#         and_(
#             Invite.code == code,
#             Invite.is_used == False,
#             Invite.expires_at > datetime.now()
#         )
#     )
#     result = await session.execute(stmt)
#     return result.scalar_one_or_none()


# async def db_mark_invite_as_used(
#     session: AsyncSession,
#     invite: Invite,
#     student_telegram_id: int
# ) -> None:
#     """Отметить приглашение как использованное"""
#     invite.is_used = True
#     invite.used_at = datetime.now()
#     invite.student_telegram_id = student_telegram_id  # Сохраняем ID ученика
#     await session.commit()
