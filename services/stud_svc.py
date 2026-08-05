# services/student_service.py

from typing import Tuple, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

# from db.crud import *
from db.models import Relationship, Invite
from db import student_crud, relp_crud, invite_crud
import secrets
from db import Student

class StudentService:
    """Сервис для работы с учениками"""

    @staticmethod
    async def create_student(
        session: AsyncSession,
        tutor_id: int,
        name: str,
        telegram_id: Optional[int] = None,
        username: Optional[str] = None,
        expires_in_days: int = 7
    ) -> Tuple[Student, Invite]:
        """Создать ученика для репетитора"""
        # 1. Проверяем репетитора
        tutor = await tutor_crud.get_by_id(session, tutor_id)
        if not tutor:
            raise ValueError("Репетитор не найден")
        
        # 2. Проверяем существующего ученика
        if telegram_id:
            existing = await student_crud.get_by_telegram_id(session, telegram_id)
            if existing:
                raise ValueError(f"Ученик с Telegram ID {telegram_id} уже существует")
        
        # 3. Создаём ученика
        student = await student_crud.create(
            session=session,
            telegram_id=telegram_id,
            first_name=name,
            username=username
        )
        
        # 4. Создаём связь
        relationship = await relp_crud.create(
            session=session,
            tutor_id=tutor_id,
            student_id=student.id
        )
        
        # 5. Создаём инвайт
        code = secrets.token_urlsafe(8)[:12]
        expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        invite = await invite_crud.create(
            session=session,
            code=code,
            tutor_id=tutor_id,
            student_name=name,
            expires_at=expires_at
        )
        
        return student, invite