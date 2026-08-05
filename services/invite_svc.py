from typing import Optional
from datetime import datetime, timedelta
import secrets
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Invite


class InviteService:
    """Сервис для работы с приглашениями"""

    @staticmethod
    async def create_invite(
        session: AsyncSession,
        tutor_id: int,
        student_name: str,
        expires_in_days: int = 1
    ) -> Invite:
        """
        Создать новое приглашение для ученика.
        
        Args:
            session: Сессия БД
            tutor_id: ID репетитора
            student_name: Имя ученика
            expires_in_days: Срок действия в днях (по умолчанию 1 день)
        
        Returns:
            Invite: Созданное приглашение
        """
        # Генерируем уникальный код
        code = secrets.token_urlsafe(8)[:12]
        
        invite = Invite(
            code=code,
            tutor_id=tutor_id,
            student_name=student_name,
            expires_at=datetime.now() + timedelta(days=expires_in_days)
        )
        
        session.add(invite)
        await session.commit()
        await session.refresh(invite)
        
        return invite

    @staticmethod
    async def get_active_invites_for_tutor(
        session: AsyncSession,
        tutor_id: int
    ) -> list[Invite]:
        """
        Получить все активные (неиспользованные и не истекшие) инвайты репетитора.
        
        Args:
            session: Сессия БД
            tutor_id: ID репетитора
        
        Returns:
            list[Invite]: Список активных инвайтов
        """
        from sqlalchemy import select, and_
        
        stmt = select(Invite).where(
            and_(
                Invite.tutor_id == tutor_id,
                Invite.is_used == False,
                Invite.expires_at > datetime.now()
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()