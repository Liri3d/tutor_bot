from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db.models import Invite
from .base_crud import BaseCRUD


class InviteCRUD(BaseCRUD[Invite]):
    """CRUD для приглашений"""

    def __init__(self):
        super().__init__(Invite)

    async def create(
        self,
        session: AsyncSession,
        code: str,
        tutor_id: int,
        student_name: str,
        expires_at: datetime
    ) -> Invite:
        invite = Invite(
            code=code,
            tutor_id=tutor_id,
            student_name=student_name,
            expires_at=expires_at,
            is_used=False
        )
        session.add(invite)
        await session.commit()
        await session.refresh(invite)
        return invite

    async def get_active_for_tutor(
        self,
        session: AsyncSession,
        tutor_id: int
    ) -> list[Invite]:
        stmt = select(Invite).where(
            and_(
                Invite.tutor_id == tutor_id,
                Invite.is_used == False,
                Invite.expires_at > datetime.now()
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
invite_crud = InviteCRUD()