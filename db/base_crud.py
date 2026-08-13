from typing import Optional, TypeVar, Generic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseCRUD(Generic[ModelType]):
    """Базовый класс для CRUD операций"""

    def __init__(self, model: ModelType):
        self.model = model

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> list[ModelType]:
        stmt = select(self.model)
        result = await session.execute(stmt)
        return result.scalars().all()