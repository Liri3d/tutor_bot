from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os

from config import BOT_ID, BOT_USERNAME

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

static_dir = os.path.join(os.path.dirname(__file__), "..", "web")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    """Главная страница - страница входа"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

@app.get("/register.html")
async def serve_register():
    """Страница регистрации"""
    file_path = os.path.join(static_dir, "register.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/dashboard.html")
async def serve_dashboard():
    """Страница дашборда"""
    file_path = os.path.join(static_dir, "dashboard.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/students.html")
async def serve_students():
    """Страница учеников"""
    file_path = os.path.join(static_dir, "students.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/lessons.html")
async def serve_lessons():
    """Страница уроков"""
    file_path = os.path.join(static_dir, "lessons.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/invites.html")
async def serve_invites():
    """Страница приглашений"""
    file_path = os.path.join(static_dir, "invites.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/settings.html")
async def serve_settings():
    """Страница настроек"""
    file_path = os.path.join(static_dir, "settings.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")





@app.post("/api/auth/register")
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Регистрация репетитора.
    """
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