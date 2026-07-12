# services/student_service.py

from typing import Tuple, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import *
from db.models import User, Relationship, Invite
from .user_service import UserService


class StudentService:
    """Сервис для работы с учениками"""

    @staticmethod
    async def register_by_invite(
        session: AsyncSession,
        telegram_id: int,
        username: str,
        first_name: str,
        invite_code: str
    ) -> Tuple[User, Relationship, User]:
        """
        Регистрация ученика по инвайт-коду.
        
        Args:
            session: Сессия БД
            telegram_id: Telegram ID пользователя
            username: Username из Telegram
            first_name: Имя из Telegram
            invite_code: Код приглашения
        
        Returns:
            tuple: (ученик, связь с репетитором, репетитор)
        
        Raises:
            ValueError: если код недействителен или пользователь уже репетитор
        """
        # 1. Проверяем инвайт
        invite = await db_get_invite_by_code(session, invite_code)
        if not invite:
            raise ValueError("❌ Недействительный код приглашения")

        # 2. Проверяем, что пользователь не репетитор
        existing_user = await db_get_user_by_telegram_id(session, telegram_id)
        if existing_user and existing_user.role == "tutor":
            raise ValueError(
                "❌ Вы зарегистрированы как репетитор.\n"
                "Чтобы подключиться как ученик, смените роль в настройках:\n"
                "Настройки → Сменить роль на ученика"
            )

        # 3. Проверяем, не подключён ли уже к этому репетитору
        if existing_user and existing_user.role == "student":
            relationship = await db_get_relationship(
                session, invite.tutor_id, existing_user.id
            )
            if relationship:
                tutor = await db_get_user_by_id(session, invite.tutor_id)
                raise ValueError(
                    f"✅ Вы уже подключены к репетитору {tutor.first_name or 'репетитору'}!"
                )

        # 4. Создаём или получаем ученика
        if not existing_user:
            student = await UserService.create_user(
                session=session,
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                role="student"
            )
        else:
            student = existing_user

        # 5. Создаём связь
        relationship = await db_create_relationship(
            session=session,
            tutor_id=invite.tutor_id,
            student_id=student.id
        )

        # 6. Отмечаем инвайт как использованный
        invite.is_used = True
        invite.used_at = datetime.now()
        invite.student_telegram_id = student.telegram_id
        await session.commit()

        # 7. Получаем репетитора для уведомления
        tutor = await db_get_user_by_id(session, invite.tutor_id)

        return student, relationship, tutor

    # @staticmethod
    # async def get_student_by_id(
    #     session: AsyncSession,
    #     student_id: int
    # ) -> Optional[User]:
    #     """
    #     Получить ученика по ID.
        
    #     Args:
    #         session: Сессия БД
    #         student_id: ID ученика
        
    #     Returns:
    #         Optional[User]: Ученик или None
    #     """
    #     return await get_user_by_id(session, student_id)

    # @staticmethod
    # async def get_student_by_telegram_id(
    #     session: AsyncSession,
    #     telegram_id: int
    # ) -> Optional[User]:
    #     """
    #     Получить ученика по Telegram ID.
        
    #     Args:
    #         session: Сессия БД
    #         telegram_id: Telegram ID пользователя
        
    #     Returns:
    #         Optional[User]: Ученик или None
    #     """
    #     user = await get_user_by_telegram_id(session, telegram_id)
    #     if user and user.role == "student":
    #         return user
    #     return None

    # @staticmethod
    # async def get_students_for_tutor(
    #     session: AsyncSession,
    #     tutor_id: int
    # ) -> List[User]:
    #     """
    #     Получить всех учеников репетитора.
        
    #     Args:
    #         session: Сессия БД
    #         tutor_id: ID репетитора
        
    #     Returns:
    #         List[User]: Список учеников
    #     """
    #     from .relationship_service import RelationshipService
    #     return await RelationshipService.get_tutor_students(session, tutor_id)

    # @staticmethod
    # async def get_students_with_balance(
    #     session: AsyncSession,
    #     tutor_id: int
    # ) -> List[dict]:
    #     """
    #     Получить учеников с информацией о балансе занятий.
        
    #     Args:
    #         session: Сессия БД
    #         tutor_id: ID репетитора
        
    #     Returns:
    #         List[dict]: [
    #             {
    #                 "user": User,
    #                 "balance": int,
    #                 "total_lessons": int,
    #                 "used_lessons": int,
    #             }
    #         ]
    #     """
    #     from .relationship_service import RelationshipService
        
    #     students = await RelationshipService.get_tutor_students(session, tutor_id)
        
    #     result = []
    #     for student in students:
    #         # Получаем активную подписку (если есть)
    #         from db.models import Subscription
    #         from sqlalchemy import select, and_
            
    #         # Находим связь
    #         relationship = await get_relationship(session, tutor_id, student.id)
    #         if not relationship:
    #             continue
            
    #         # Находим активную подписку
    #         stmt = select(Subscription).where(
    #             and_(
    #                 Subscription.relationship_id == relationship.id,
    #                 Subscription.expires_at > datetime.now()
    #             )
    #         )
    #         sub_result = await session.execute(stmt)
    #         subscription = sub_result.scalar_one_or_none()
            
    #         if subscription:
    #             result.append({
    #                 "user": student,
    #                 "balance": subscription.balance,
    #                 "total_lessons": subscription.total_lessons,
    #                 "used_lessons": subscription.used_lessons,
    #             })
    #         else:
    #             result.append({
    #                 "user": student,
    #                 "balance": 0,
    #                 "total_lessons": 0,
    #                 "used_lessons": 0,
    #             })
        
    #     return result

    # @staticmethod
    # async def has_active_relationship(
    #     session: AsyncSession,
    #     student_id: int,
    #     tutor_id: int
    # ) -> bool:
    #     """
    #     Проверить, есть ли активная связь между учеником и репетитором.
        
    #     Args:
    #         session: Сессия БД
    #         student_id: ID ученика
    #         tutor_id: ID репетитора
        
    #     Returns:
    #         bool: True, если связь активна
    #     """
    #     relationship = await get_relationship(session, tutor_id, student_id)
    #     return relationship is not None and relationship.status == "active"