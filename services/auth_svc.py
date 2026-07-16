import secrets
import hashlib
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db import tutor_crud
from db import student_crud
from db.models import Tutor, Student


class AuthService:
    """Сервис для регистрации и входа"""

    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}:{hash_obj}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            salt, stored_hash = password_hash.split(':')
            calculated_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            return calculated_hash == stored_hash
        except:
            return False

    @staticmethod
    async def register_tutor(
        session: AsyncSession,
        login: str,
        password: str,
        first_name: str,
        username: Optional[str] = None
    ) -> Tutor:
        """Регистрация репетитора"""
        existing = await tutor_crud.get_by_login(session, login)
        if existing:
            raise ValueError("Логин уже занят")
        
        password_hash = AuthService.hash_password(password)
        tutor = await tutor_crud.create(
            session=session,
            login=login,
            password_hash=password_hash,
            first_name=first_name,
            username=username
        )
        return tutor

    @staticmethod
    async def login_tutor(
        session: AsyncSession,
        login: str,
        password: str
    ) -> Tutor:
        """Вход репетитора"""
        tutor = await tutor_crud.get_by_login(session, login)
        if not tutor:
            raise ValueError("Неверный логин или пароль")
        
        if not AuthService.verify_password(password, tutor.password_hash):
            raise ValueError("Неверный логин или пароль")
        
        return tutor

    @staticmethod
    async def register_student(
        session: AsyncSession,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Student:
        """Регистрация ученика через Telegram"""
        existing = await student_crud.get_by_telegram_id(session, telegram_id)
        if existing:
            raise ValueError("Пользователь с таким Telegram ID уже существует")
        
        student = await student_crud.create(
            session=session,
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
            phone=phone
        )
        return student
