from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Tutor
from .base_crud import BaseCRUD


class TutorCRUD(BaseCRUD[Tutor]):
    """CRUD для репетиторов"""

    def __init__(self):
        super().__init__(Tutor)

    async def get_by_telegram_id(self, session: AsyncSession, telegram_id: int) -> Optional[Tutor]:
        stmt = select(Tutor).where(Tutor.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> Tutor:
        tutor = Tutor(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )
        session.add(tutor)
        await session.commit()
        await session.refresh(tutor)
        return tutor

tutor_crud = TutorCRUD()