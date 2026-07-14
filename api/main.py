# api/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

import os
from datetime import datetime

from services import *
from api.schemas import (
    UserResponse,
    StudentResponse,
    LessonResponse,
    InviteResponse,
    TutorStatsResponse,
)

app = FastAPI(
    title="Tutor Bot API",
    description="API для управления расписанием репетитора",
    version="1.0.0"
)

# CORS для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== СТАТИЧЕСКИЕ ФАЙЛЫ ==========

# Для простоты используем HTML, CSS, JS в папке web/
static_dir = os.path.join(os.path.dirname(__file__), "..", "web")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_index():
    """Главная страница"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Web client not found. Please build the frontend."}


# # ========== API ЭНДПОИНТЫ ==========

@app.get("/api/tutors/{telegram_id}/students", response_model=List[StudentResponse])
async def get_tutor_students(
    telegram_id: int,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Получить всех учеников репетитора.
    """
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Репетитор не найден"
        )
    
    students = await RelationshipService.get_tutor_students(session, tutor.id)
    
    return [
        StudentResponse(
            id=student.id,
            telegram_id=student.telegram_id,
            first_name=student.first_name or "Без имени",
            username=student.username,
            registered_at=student.registered_at
        )
        for student in students
    ]


@app.get("/api/tutors/{telegram_id}/stats", response_model=TutorStatsResponse)
async def get_tutor_stats(
    telegram_id: int,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Получить статистику репетитора.
    """
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Репетитор не найден"
        )
    
    students = await RelationshipService.get_tutor_students(session, tutor.id)
    
    # Здесь можно добавить подсчёт занятий за неделю/месяц
    
    return TutorStatsResponse(
        total_students=len(students),
        active_students=len(students),  # упрощённо
        lessons_this_week=0,  # TODO: подсчёт
        lessons_this_month=0,  # TODO: подсчёт
    )


@app.get("/api/tutors/{telegram_id}/lessons", response_model=List[LessonResponse])
async def get_tutor_lessons(
    telegram_id: int,
    date_from: str = None,
    date_to: str = None,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Получить занятия репетитора.
    """
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Репетитор не найден"
        )
    
    # TODO: реализовать получение занятий
    return []


@app.get("/api/tutors/{telegram_id}/invites", response_model=List[InviteResponse])
async def get_tutor_invites(
    telegram_id: int,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Получить активные приглашения репетитора.
    """
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Репетитор не найден"
        )
    
    from services import InviteService
    invites = await InviteService.get_active_invites_for_tutor(session, tutor.id)
    
    return [
        InviteResponse(
            code=invite.code,
            student_name=invite.student_name,
            expires_at=invite.expires_at,
            is_used=invite.is_used
        )
        for invite in invites
    ]


# @app.post("/api/tutors/{telegram_id}/invites")
# async def create_invite(
#     telegram_id: int,
#     student_name: str,
#     session: AsyncSession = Depends(SessionService.get_session)
# ):
#     """
#     Создать приглашение для ученика.
#     """
#     tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
#     if not tutor or tutor.role != "tutor":
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Репетитор не найден"
#         )
    
#     from services import InviteService
#     invite = await InviteService.create_invite(
#         session=session,
#         tutor_id=tutor.id,
#         student_name=student_name,
#         expires_in_days=1
#     )
    
#     return {
#         "code": invite.code,
#         "student_name": invite.student_name,
#         "expires_at": invite.expires_at,
#         "link": f"https://t.me/tutortesting_bot?start=invite_{invite.code}"
#     }


@app.get("/api/tutors/{telegram_id}/check")
async def check_tutor_exists(
    telegram_id: int,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Проверить, существует ли репетитор с таким Telegram ID.
    """
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        return {"exists": False}
    
    return {
        "exists": True,
        "name": tutor.first_name or "Репетитор",
        "students_count": len(await RelationshipService.get_tutor_students(session, tutor.id))
    }