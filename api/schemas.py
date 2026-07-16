# api/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class UserResponse(BaseModel):
    """Ответ с информацией о пользователе"""
    id: int
    telegram_id: int
    first_name: str
    username: Optional[str]
    role: str
    registered_at: datetime


class StudentResponse(BaseModel):
    """Ответ с информацией об ученике"""
    id: int
    telegram_id: int
    first_name: str
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

class RegisterRequest(BaseModel):
    login: str  
    password: str
    first_name: str
    role: str = "tutor" 

class LoginRequest(BaseModel):
    login: str
    password: str