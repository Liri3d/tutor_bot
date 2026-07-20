# services/user_svc.py
import hashlib
import secrets
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Tutor, Student
from db.tutor_crud import tutor_crud
from db.student_crud import student_crud


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    async def create_user(
        session: AsyncSession,
        telegram_id: int,
        role: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None
    ) -> User:
        """
        Создать нового пользователя.
        """
        # Для репетитора создаем запись в Tutor
        if role == "tutor" and login and password:
            # Проверяем, не занят ли логин
            existing = await tutor_crud.get_by_login(session, login)
            if existing:
                raise ValueError(f"Логин {login} уже занят")
            
            # Хэшируем пароль
            salt = secrets.token_hex(16)
            hash_obj = hashlib.sha256((salt + password).encode()).hexdigest()
            password_hash = f"{salt}:{hash_obj}"
            
            # Создаем репетитора
            tutor = await tutor_crud.create(
                session=session,
                login=login,
                password_hash=password_hash,
                first_name=first_name or "Репетитор",
                username=username
            )
            return tutor
        
        # Для ученика создаем запись в Student
        if role == "student":
            existing = await student_crud.get_by_telegram_id(session, telegram_id)
            if existing:
                raise ValueError(f"Пользователь с Telegram ID {telegram_id} уже существует")
            
            student = await student_crud.create(
                session=session,
                telegram_id=telegram_id,
                first_name=first_name or "Ученик",
                username=username
            )
            return student
        
        raise ValueError(f"Неизвестная роль: {role}")

    @staticmethod
    async def get_user_by_telegram_id(
        session: AsyncSession,
        telegram_id: int
    ) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        # Ищем в Student
        student = await student_crud.get_by_telegram_id(session, telegram_id)
        if student:
            return student
        
        # Если не нашли, можно добавить поиск по username
        return None

    @staticmethod
    async def get_user_by_login(
        session: AsyncSession,
        login: str
    ) -> Optional[User]:
        """Получить пользователя по логину"""
        tutor = await tutor_crud.get_by_login(session, login)
        if tutor:
            return tutor
        return None

    @staticmethod
    async def get_user_by_id(
        session: AsyncSession,
        user_id: int
    ) -> Optional[User]:
        """Получить пользователя по ID"""
        # Сначала ищем в Tutor
        tutor = await tutor_crud.get_by_id(session, user_id)
        if tutor:
            return tutor
        
        # Потом в Student
        student = await student_crud.get_by_id(session, user_id)
        if student:
            return student
        
        return None

    @staticmethod
    async def is_tutor(
        session: AsyncSession,
        telegram_id: int
    ) -> bool:
        """Проверить, является ли пользователь репетитором"""
        user = await UserService.get_user_by_telegram_id(session, telegram_id)
        return user is not None and user.role == "tutor"

    @staticmethod
    async def is_student(
        session: AsyncSession,
        telegram_id: int
    ) -> bool:
        """Проверить, является ли пользователь учеником"""
        user = await UserService.get_user_by_telegram_id(session, telegram_id)
        return user is not None and user.role == "student"
    
    @staticmethod
    async def change_role(
        session: AsyncSession,
        user: User
    ) -> User:
        """Сменить роль пользователя"""
        # Реализация смены роли
        pass