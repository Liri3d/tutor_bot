from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from db.crud import get_user_by_telegram_id, get_tutor_students
from db.models import User

app = FastAPI(title="Tutor Bot API", version="1.0.0")

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы для фронтенда
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Tutor Bot API", "status": "running"}


@app.get("/api/users/{telegram_id}")
async def get_user(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Получить пользователя по Telegram ID"""
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "role": user.role
    }


@app.get("/api/tutors/{tutor_id}/students")
async def get_students(
    tutor_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Получить всех учеников репетитора"""
    tutor = await get_user_by_telegram_id(session, tutor_id)
    if not tutor or tutor.role != 'tutor':
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    students = await get_tutor_students(session, tutor_id)
    return [
        {
            "id": s.id,
            "telegram_id": s.telegram_id,
            "username": s.username,
            "first_name": s.first_name
        }
        for s in students
    ]