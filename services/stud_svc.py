# services/student_service.py

from typing import Tuple, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Invite
from db import student_crud, invite_crud, tutor_crud
from db import link_crud


class StudentService:
    """Сервис для работы с учениками"""

    pass

    # @staticmethod
    # async def register_by_invite(
    #     session: AsyncSession,
    #     telegram_id: int,
    #     username: Optional[str],
    #     first_name: str,
    #     invite_code: str
    # ) -> Tuple:
    #     """
    #     Регистрация ученика по инвайт-коду.
        
    #     Args:
    #         session: Сессия БД
    #         telegram_id: Telegram ID пользователя
    #         username: Username Telegram
    #         first_name: Имя пользователя
    #         invite_code: Код приглашения
            
    #     Returns:
    #         Tuple[Student, Relationship, Tutor]: Ученик, Связь, Репетитор
            
    #     Raises:
    #         ValueError: Если инвайт не найден, истёк или уже использован
    #     """
    #     # 1. Находим активный инвайт
    #     invite = await invite_crud.get_active_for_tutor(session, None)
        
    #     # 2. Проверяем, не использован ли уже
    #     if invite.is_used:
    #         raise ValueError("Это приглашение уже было использовано")
        
    #     # 3. Проверяем, не истёк ли
    #     if invite.expires_at < datetime.now():
    #         raise ValueError("Срок действия приглашения истёк")
        
    #     # 4. Создаём или получаем ученика
    #     student = await student_crud.get_by_telegram_id(session, telegram_id)
    #     if not student:
    #         student = await student_crud.create(
    #             session=session,
    #             telegram_id=telegram_id,
    #             first_name=first_name,
    #             username=username
    #         )
        
    #     # 5. Создаём связь
    #     existing_rel = await link_crud.get_by_tutor_and_student(
    #         session, invite.tutor_id, student.id
    #     )
    #     if not existing_rel:
    #         await link_crud.create(
    #             session=session,
    #             tutor_id=invite.tutor_id,
    #             student_id=student.id
    #         )
        
    #     # 6. Помечаем инвайт как использованный
    #     invite.is_used = True
    #     invite.used_at = datetime.now()
    #     await session.commit()
        
    #     # 7. Получаем репетитора
    #     tutor = await tutor_crud.get_by_id(session, invite.tutor_id)
        
    #     return student, existing_rel or link_crud.last_created, tutor
