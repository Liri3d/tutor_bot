# api/schemas.py
from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import Optional, List
import re


class UserResponse(BaseModel):
    """Ответ с информацией о пользователе"""
    id: int
    telegram_id: int
    name: str
    username: Optional[str]
    role: str
    registered_at: datetime


class StudentResponse(BaseModel):
    """Ответ с информацией об ученике"""
    id: int
    telegram_id: int
    name: str
    username: Optional[str]
    registered_at: datetime


class LessonResponse(BaseModel):
    """Ответ с информацией о занятии"""
    id: int
    start_time: datetime
    duration_minutes: int
    subject: Optional[str]
    status: str
    paid: bool


class InviteResponse(BaseModel):
    """Ответ с информацией о приглашении"""
    code: str
    student_name: str
    expires_at: datetime
    is_used: bool
    link: Optional[str] = None


class TutorStatsResponse(BaseModel):
    """Статистика репетитора"""
    total_students: int
    active_students: int
    lessons_this_week: int
    lessons_this_month: int


# ===== ВХОДНЫЕ СХЕМЫ С ВАЛИДАЦИЕЙ =====

class RegisterRequest(BaseModel):
    """Схема регистрации репетитора"""
    login: str = Field(..., min_length=3, max_length=50, description="Логин пользователя")
    password: str = Field(..., min_length=6, max_length=128, description="Пароль пользователя")
    name: str = Field(..., min_length=2, max_length=100, description="Имя пользователя")

    @field_validator('login')
    @classmethod
    def validate_login(cls, v: str) -> str:
        """Валидация логина: только латиница, цифры и_UNDERSCORE_"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Логин может содержать только латинские буквы, цифры и символ подчёркивания')
        if len(v) < 3:
            raise ValueError('Логин должен содержать минимум 3 символа')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация пароля: минимум 6 символов, хотя бы одна буква и одна цифра"""
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидация имени: минимум 2 символа"""
        if len(v.strip()) < 2:
            raise ValueError('Имя должно содержать минимум 2 символа')
        return v.strip()


class LoginRequest(BaseModel):
    """Схема входа в систему"""
    login: str = Field(..., min_length=3, max_length=50, description="Логин пользователя")
    password: str = Field(..., min_length=6, max_length=128, description="Пароль пользователя")


class LoginResponse(BaseModel):
    """Ответ после успешного входа"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    login: str
    name: str
    role: str = "tutor"
