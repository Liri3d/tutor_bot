# api/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import hashlib
import hmac
import os
from datetime import datetime, timedelta
from telegram.error import InvalidToken 

from config import BOT_ID, BOT_USERNAME, ENVIRONMENT
from services import *
from api.schemas import *

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

# ========== ПУТИ ДЛЯ СТАТИКИ ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

print(f"📁 BASE_DIR: {BASE_DIR}")
print(f"📁 FRONTEND_DIST: {FRONTEND_DIST}")
print(f"📁 FRONTEND_DIST exists: {os.path.exists(FRONTEND_DIST)}")
print(f"📁 ENVIRONMENT: {ENVIRONMENT}")

# ========== РЕЖИМ РАЗРАБОТКИ ==========
IS_DEV = ENVIRONMENT == "development"




# ========== API ЭНДПОИНТЫ ==========

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Tutor Flow API is running"}

@app.get("/api/tutors/{telegram_id}/students", response_model=List[StudentResponse])
async def get_tutor_students(
    telegram_id: int,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """Получить всех учеников репетитора."""
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
    """Получить статистику репетитора."""
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Репетитор не найден"
        )
    
    students = await RelationshipService.get_tutor_students(session, tutor.id)
    
    return TutorStatsResponse(
        total_students=len(students),
        active_students=len(students),
        lessons_this_week=0,
        lessons_this_month=0,
    )

@app.get("/api/tutors/{telegram_id}/lessons", response_model=List[LessonResponse])
async def get_tutor_lessons(
    telegram_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """Получить занятия репетитора."""
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Репетитор не найден"
        )
    
    return []

@app.get("/api/tutors/{telegram_id}/invites", response_model=List[InviteResponse])
async def get_tutor_invites(
    telegram_id: int,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """Получить активные приглашения репетитора."""
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
    """Создать приглашение для ученика."""
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
    """Проверить, существует ли репетитор с таким Telegram ID."""
    tutor = await UserService.get_user_by_telegram_id(session, telegram_id)
    if not tutor or tutor.role != "tutor":
        return {"exists": False}
    
    return {
        "exists": True,
        "name": tutor.first_name or "Репетитор",
        "students_count": len(await RelationshipService.get_tutor_students(session, tutor.id))
    }

@app.get("/api/bot/info")
async def get_bot_info():
    """Получить информацию о боте"""
    return {
        "id": BOT_ID,
        "username": BOT_USERNAME,
        "is_initialized": BOT_ID is not None
    }

# ========== АВТОРИЗАЦИЯ ==========

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
    """Обработка callback от Telegram OAuth."""
    from config import BOT_TOKEN
    
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

        if not verify_telegram_auth(data.copy(), BOT_TOKEN):
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
    except InvalidToken:
        print("❌ Недействительный токен бота!")
        raise HTTPException(status_code=500, detail="Invalid bot token")
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
    
    auth_time = datetime.fromtimestamp(auth_date)
    if datetime.now() - auth_time > timedelta(hours=24):
        print("❌ Авторизация истекла")
        raise HTTPException(status_code=401, detail="Authorization expired")
    
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

@app.post("/api/auth/register")
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """Регистрация репетитора."""
    try:
        tutor = await AuthService.register_tutor(
            session=session,
            login=request.login,
            password=request.password,
            first_name=request.first_name
        )
        return {
            "status": "registered",
            "id": tutor.id,
            "login": tutor.login,
            "first_name": tutor.first_name,
            "role": "tutor",
            "message": "✅ Регистрация успешна!"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """Вход репетитора"""
    try:
        tutor = await AuthService.login_tutor(
            session=session,
            login=request.login,
            password=request.password
        )
        return {
            "status": "authenticated",
            "id": tutor.id,
            "login": tutor.login,
            "first_name": tutor.first_name,
            "role": "tutor",
            "message": f"👋 Добро пожаловать, {tutor.first_name}!"
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# ========== FRONTEND (React SPA) ==========

# Если режим разработки - пробуем проксировать на Vite
if IS_DEV:
    try:
        import httpx
        print("🔧 Режим разработки: проксируем запросы на Vite (http://localhost:5173)")
        
        @app.get("/")
        @app.get("/{full_path:path}")
        async def proxy_to_vite(full_path: str = ""):
            # API запросы пропускаем
            if full_path.startswith("api/") or full_path.startswith("auth/"):
                raise HTTPException(status_code=404)
            
            # Проксируем на Vite
            async with httpx.AsyncClient(timeout=10.0) as client:  # Добавили timeout
                try:
                    # Пробуем подключиться к Vite
                    url = f"http://127.0.0.1:5173/{full_path}"  # Изменили localhost на 127.0.0.1
                    print(f"🔄 Прокси: {url}")
                    response = await client.get(url)
                    return HTMLResponse(
                        content=response.text,
                        status_code=response.status_code
                    )
                except httpx.ConnectError:
                    print("❌ Vite не запущен на порту 5173")
                    return HTMLResponse(
                        content="""
                        <html>
                            <body style="font-family: Arial; padding: 40px; text-align: center;">
                                <h1>⚠️ Frontend не запущен</h1>
                                <p>Запустите frontend командой:</p>
                                <code style="background: #f1f5f9; padding: 10px; display: inline-block; border-radius: 8px;">
                                    cd frontend && npm run dev -- --host 0.0.0.0
                                </code>
                                <p style="margin-top: 20px;">Или используйте production режим: <code>ENVIRONMENT=production</code></p>
                            </body>
                        </html>
                        """,
                        status_code=503
                    )
                except Exception as e:
                    print(f"❌ Ошибка прокси: {e}")
                    return HTMLResponse(
                        content=f"<h1>Ошибка: {str(e)}</h1>",
                        status_code=500
                    )
    except ImportError:
        print("⚠️ httpx не установлен. Установите: pip install httpx")
        # Если httpx нет - пробуем использовать dist
        if os.path.exists(FRONTEND_DIST):
            app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
            
            @app.get("/")
            async def serve_index():
                return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
            
            @app.get("/{full_path:path}")
            async def serve_react(full_path: str):
                if full_path.startswith("api/") or full_path.startswith("auth/"):
                    raise HTTPException(status_code=404)
                
                file_path = os.path.join(FRONTEND_DIST, full_path)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    return FileResponse(file_path)
                
                return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
        else:
            @app.get("/")
            async def serve_index_dev():
                return HTMLResponse("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Tutor Bot API</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #F8FAFC; }
                        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                        h1 { color: #1E293B; }
                        .status { color: #10B981; font-weight: bold; }
                        .warning { background: #FEF3C7; padding: 15px; border-radius: 8px; margin: 20px 0; }
                        code { background: #F1F5F9; padding: 2px 6px; border-radius: 4px; }
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h1>📚 Tutor Bot API</h1>
                        <p><span class="status">✅ API работает</span></p>
                        <div class="warning">
                            <strong>⚠️ Frontend не доступен!</strong>
                            <p>Установите httpx или запустите frontend:</p>
                            <code>cd frontend && npm run dev</code>
                        </div>
                        <p style="color:#64748B;">📖 Документация: <code>/docs</code></p>
                    </div>
                </body>
                </html>
                """)
else:
    # Production режим - обслуживаем статику из dist
    if os.path.exists(FRONTEND_DIST):
        print("📁 Production режим: обслуживаем статику из dist")
        app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
        
        @app.get("/")
        async def serve_index():
            return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
        
        @app.get("/{full_path:path}")
        async def serve_react(full_path: str):
            if full_path.startswith("api/") or full_path.startswith("auth/"):
                raise HTTPException(status_code=404)
            
            file_path = os.path.join(FRONTEND_DIST, full_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(file_path)
            
            return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
    else:
        @app.get("/")
        async def serve_index_dev():
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Tutor Bot API</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #F8FAFC; }
                    .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                    h1 { color: #1E293B; }
                    .status { color: #10B981; font-weight: bold; }
                    .warning { background: #FEF3C7; padding: 15px; border-radius: 8px; margin: 20px 0; }
                    code { background: #F1F5F9; padding: 2px 6px; border-radius: 4px; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>📚 Tutor Bot API</h1>
                    <p><span class="status">✅ API работает</span></p>
                    <div class="warning">
                        <strong>⚠️ Frontend не собран!</strong>
                        <p>Чтобы увидеть React-интерфейс, выполните:</p>
                        <code>cd frontend && npm run build</code>
                    </div>
                    <p style="color:#64748B;">📖 Документация: <code>/docs</code></p>
                </div>
            </body>
            </html>
            """)