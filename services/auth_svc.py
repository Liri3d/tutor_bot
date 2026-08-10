# services/auth_svc.py
import secrets
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.tutor_crud import tutor_crud
from db.models import Tutor

# Настройка bcrypt через passlib — криптографически стойкая альтернатива hashlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Сервис для регистрации и входа"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Хеширование пароля с использованием bcrypt.
        
        Bcrypt автоматически генерирует соль и включает cost factor,
        что делает его устойчивым к брутфорсу и rainbow table атакам.
        
        Args:
            password: Пароль в открытом виде
            
        Returns:
            str: Хеш пароля в формате bcrypt
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Проверка пароля против хеша.
        
        Args:
            password: Пароль в открытом виде
            password_hash: Хеш пароля (bcrypt формат)
            
        Returns:
            bool: True если пароль совпал
        """
        # Если хеш не в формате bcrypt (старый format salt:hash),
        # пытаемся распарсить и проверить через старый метод
        if ':' in password_hash and not password_hash.startswith('$2'):
            try:
                salt, stored_hash = password_hash.split(':', 1)
                import hashlib
                calculated_hash = hashlib.sha256((salt + password).encode()).hexdigest()
                return calculated_hash == stored_hash
            except:
                return False
        
        return pwd_context.verify(password, password_hash)

    @staticmethod
    async def register_tutor(
        session: AsyncSession,
        login: str,
        password: str,
        name: str
    ) -> Tutor:
        """Регистрация репетитора"""
        existing = await tutor_crud.get_by_login(session, login)
        if existing:
            raise ValueError("Логин уже занят")
        
        # Используем bcrypt для хеширования
        password_hash = AuthService.hash_password(password)
        
        tutor = await tutor_crud.create(
            session=session,
            login=login,
            password_hash=password_hash,
            name=name
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
