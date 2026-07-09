from sqlalchemy.ext.asyncio import AsyncSession

from services import get_or_create_user
from services.relationship_service import register_student_by_invite as service_register_student
from db.models import User, Relationship  # ← ДОБАВЬ ЭТУ СТРОКУ


async def register_tutor(
    session: AsyncSession,
    telegram_id: int,
    username: str,
    first_name: str
) -> User:  # ← Теперь интерпретатор знает, что такое User
    """Регистрация репетитора через сервис"""
    return await get_or_create_user(
        session=session,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        role='tutor'
    )


async def register_student_by_invite(
    session: AsyncSession,
    telegram_id: int,
    username: str,
    first_name: str,
    invite_code: str
) -> tuple[User, Relationship]:  # ← Теперь всё работает
    """Регистрация ученика через сервис"""
    return await service_register_student(
        session=session,
        telegram_id=telegram_id,
        invite_code=invite_code,
        username=username,
        first_name=first_name
    )