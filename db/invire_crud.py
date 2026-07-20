from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Invite
from .base_crud import BaseCRUD


class InviteCRUD(BaseCRUD[Invite]):
    """CRUD для приглашений"""

    def __init__(self):
        super().__init__(Invite)

    async def create(
        self,
        session: AsyncSession,
        login: str,
        password_hash: str,
        first_name: str,
        username: Optional[str] = None
    ) -> Invite:
        invite = Invite(
            login=login,
            password_hash=password_hash,
            first_name=first_name,
            username=username,
            role="invite"
        )
        session.add(invite)
        await session.commit()
        await session.refresh(invite)
        return invite

invite_crud = InviteCRUD()