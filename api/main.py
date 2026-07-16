# api/main.py

from aiogram import Bot
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import hashlib
import hmac
import os
from datetime import datetime
from telegram.error import InvalidToken 

from config import BOT_ID, BOT_USERNAME

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
            is_used=invite.is_used,
            link=f"https://t.me/{BOT_USERNAME}?start=invite_{invite.code}"
        )
        for invite in invites
    ]


@app.post("/api/tutors/{telegram_id}/invites")
async def create_invite(
    telegram_id: int,
    student_name: str,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Создать приглашение для ученика.
    """
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Репетитор не найден"
        )
    
    from services import InviteService
    invite = await InviteService.create_invite(
        session=session,
        tutor_id=tutor.id,
        student_name=student_name,
        expires_in_days=1
    )
    
    return {
        "code": invite.code,
        "student_name": invite.student_name,
        "expires_at": invite.expires_at,
        "link": f"https://t.me/{BOT_USERNAME}?start=invite_{invite.code}"
    }

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


@app.get("/auth")
async def auth_page():
    """Страница обработки авторизации"""
    auth_path = os.path.join(static_dir, "auth.html")
    if os.path.exists(auth_path):
        return FileResponse(auth_path)
    return {"message": "Auth page not found"}









def verify_telegram_auth(data: dict, bot_token: str) -> bool:
    """Ручная проверка подписи Telegram OAuth"""
    received_hash = data.pop('hash', None)
    if not received_hash:
        return False
    
    sorted_data = sorted(data.items())
    data_string = "\n".join([f"{k}={v}" for k, v in sorted_data])
    
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_string.encode(), hashlib.sha256)
    calculated_hash = hmac_hash.hexdigest()
    
    return calculated_hash == received_hash

@app.get("/api/auth/telegram")
async def telegram_auth_callback(
    id: int = None,
    first_name: str = None,
    username: str = None,
    photo_url: str = None,
    auth_date: int = None,
    hash: str = None
):
    """
    Обработка callback от Telegram OAuth.
    """
    from config import BOT_TOKEN
    
    # ===== 1. Проверяем наличие параметров =====
    missing_params = []
    if not id: missing_params.append("id")
    if not first_name: missing_params.append("first_name")
    if not auth_date: missing_params.append("auth_date")
    if not hash: missing_params.append("hash")
    
    if missing_params:
        print(f"❌ Отсутствуют параметры: {missing_params}")
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required parameters: {', '.join(missing_params)}"
        )
    
    print(f"🔍 Проверка авторизации для: @{username or first_name} (id={id})")
    
    # ===== 2. Проверяем подпись =====
    try:
        data = {
            "id": id,
            "first_name": first_name,
            "auth_date": auth_date,
        }
        if username:
            data["username"] = username
        if photo_url:
            data["photo_url"] = photo_url
        
        # bot = Bot(token=BOT_TOKEN)
        
        # if not bot.check_authorization(data):
        #     print("❌ Недействительная подпись!")
        #     raise HTTPException(status_code=401, detail="Invalid authentication")
            
        # print("✅ Подпись подтверждена!")

        if not verify_telegram_auth(data.copy(), BOT_TOKEN):
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
    except InvalidToken:
        print("❌ Недействительный токен бота!")
        raise HTTPException(status_code=500, detail="Invalid bot token")
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
    
    # ===== 3. Проверяем срок действия =====
    from datetime import datetime, timedelta
    auth_time = datetime.fromtimestamp(auth_date)
    if datetime.now() - auth_time > timedelta(hours=24):
        print("❌ Авторизация истекла")
        raise HTTPException(status_code=401, detail="Authorization expired")
    
    # ===== 4. Ищем или создаём пользователя =====
    async for session in SessionService.get_session():
        user = await UserService.get_user_by_telegram_id(session, id)
        
        if not user:
            user = await UserService.create_user(
                session=session,
                telegram_id=id,
                username=username,
                first_name=first_name,
                role="student"
            )
            print(f"✅ Создан новый пользователь: @{user.username or user.first_name}")
            return {
                "status": "registered",
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "username": user.username,
                "role": user.role,
                "message": "✅ Аккаунт создан!"
            }
        
        print(f"✅ Найден пользователь: @{user.username or user.first_name}")
        return {
            "status": "authenticated",
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "username": user.username,
            "role": user.role,
            "message": f"👋 С возвращением, {user.first_name}!"
        }
    

@app.get("/api/bot/info")
async def get_bot_info():
    """Получить информацию о боте"""
    return {
        "id": BOT_ID,
        "username": BOT_USERNAME,
        "is_initialized": BOT_ID is not None
    }