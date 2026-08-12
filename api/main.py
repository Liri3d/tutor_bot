# api/main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import httpx

from config import BOT_ID, BOT_USERNAME, ENVIRONMENT

from services import *
from api.schemas import *
# from api.jwt_handler import (
#     create_access_token,
#     get_current_user,
#     JWT_SECRET_KEY
# )

app = FastAPI(
    title="Tutor Bot API",
    description="API для управления расписанием репетитора",
    version="1.0.0"
)

# CORS — в продакшене разрешаем только доверенные домены
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8000")
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", frontend_url).split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Статические файлы
static_dir = os.path.join(os.path.dirname(__file__), "..", "web")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# # Логирование при запуске
# print(f"🔐 JWT_SECRET_KEY configured: {'yes' if JWT_SECRET_KEY else 'no'}")
# print(f"🌐 CORS origins: {allowed_origins}")
# print(f"🔧 Environment: {ENVIRONMENT}")


# ===== СТРАНИЦЫ =====

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


# ===== AUTH ENDPOINTS =====

@app.post("/api/auth/register")
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Регистрация репетитора.
    
    Возвращает:
    - status: registered
    - user_id: ID репетитора
    - message: Сообщение об успехе
    """
    try:
        tutor = await AuthService.register_tutor(
            session=session,
            login=request.login,
            password=request.password,
            name=request.name
        )
        return {
            "status": "registered",
            "user_id": tutor.id,
            "login": tutor.login,
            "name": tutor.name,
            "message": "✅ Регистрация успешна! Теперь вы можете войти."
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(SessionService.get_session)
):
    """
    Вход репетитора. Возвращает JWT access токен.
    
    Args:
        login: Логин репетитора
        password: Пароль
        
    Returns:
        JWT токен для последующих запросов
    """
    try:
        tutor = await AuthService.login_tutor(
            session=session,
            login=request.login,
            password=request.password
        )
        
        # Создаём JWT токен
        access_token = create_access_token(
            data={
                "sub": str(tutor.id),
                "role": "tutor",
                "login": tutor.login,
                "name": tutor.name
            }
        )
        
        return LoginResponse(
            access_token=access_token,
            user_id=tutor.id,
            login=tutor.login,
            name=tutor.name,
            role="tutor"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


# ===== ЗАЩИЩЁННЫЕ ЭНДПОИНТЫ (примеры) =====

# @app.get("/api/tutors/me")
# async def get_current_tutor_info(current_user: dict = Depends(get_current_user)):
#     """
#     Получить информацию о текущем пользователе.
#     Этот эндпоинт защищён — требует JWT токен.
#     """
#     return {
#         "user_id": int(current_user["sub"]),
#         "login": current_user.get("login"),
#         "name": current_user.get("name"),
#         "role": current_user.get("role")
#     }










SQLITE_WEB_PORT = 8080

@app.api_route("/sqlite-web/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "HEAD"])
async def proxy_sqlite_all(request: Request, path: str):
    """Проксирует ВСЕ запросы к sqlite-web (GET, POST и т.д.)"""
    url = f"http://localhost:{SQLITE_WEB_PORT}/{path}"
    
    # Добавляем query параметры
    if request.query_params:
        url += f"?{request.query_params}"
    
    # Получаем тело запроса (для POST)
    body = await request.body()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=body if body else None
            )
            
            # Возвращаем ответ
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.ConnectError:
            return Response(
                content=f"❌ Не удалось подключиться к sqlite-web на порту {SQLITE_WEB_PORT}",
                status_code=503
            )
        except Exception as e:
            return Response(
                content=f"❌ Ошибка прокси: {str(e)}",
                status_code=500
            )

@app.get("/sqlite-web")
async def proxy_sqlite_root():
    """Перенаправление на корень sqlite-web"""
    return RedirectResponse(url="/sqlite-web/")

@app.get("/sqlite-web/")
async def proxy_sqlite_root_slash():
    """Корень sqlite-web"""
    return await proxy_sqlite_all(Request(scope={"type": "http", "method": "GET"}), "")

@app.get("/debug-sqlite")
async def debug_sqlite():
    """Проверка, что sqlite-web доступен"""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/")
            return {
                "status": "ok",
                "status_code": response.status_code,
                "content_length": len(response.content),
                "content_preview": response.text[:200] if response.text else "empty"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }