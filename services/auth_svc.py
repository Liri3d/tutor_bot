# services/auth_svc.py
import secrets
import hashlib
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.tutor_crud import tutor_crud

from db.models import Tutor


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
        first_name: str
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
            first_name=first_name
        )
        return tutor

    @staticmethod
    async def login_tutor(
        session: AsyncSession,
        login: str,
        password: str
    ) -> Tutor:  # ← возвращаем Tutor
        """Вход репетитора"""
        tutor = await tutor_crud.get_by_login(session, login)
        if not tutor:
            raise ValueError("Неверный логин или пароль")
        
        if not AuthService.verify_password(password, tutor.password_hash):
            raise ValueError("Неверный логин или пароль")
        
        return tutor  # ← возвращаем Tutor, а не User