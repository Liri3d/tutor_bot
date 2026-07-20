from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Tutor
from .base_crud import BaseCRUD


class TutorCRUD(BaseCRUD[Tutor]):
    """CRUD для репетиторов"""

    def __init__(self):
        super().__init__(Tutor)

    async def get_by_login(self, session: AsyncSession, login: str) -> Optional[Tutor]:
        stmt = select(Tutor).where(Tutor.login == login)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        login: str,
        password_hash: str,
        first_name: str,
        username: Optional[str] = None
    ) -> Tutor:
        tutor = Tutor(
            login=login,
            password_hash=password_hash,
            first_name=first_name,
            username=username,
        )
        session.add(tutor)
        await session.commit()
        await session.refresh(tutor)
        return tutor

tutor_crud = TutorCRUD()