import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from .models import Base

# Берём путь к БД из .env или используем по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tutor_bot.db")

# Создаём асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # True — показывает SQL-запросы в консоли (полезно для отладки)
)

# Создаём фабрику сессий
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def init_db():
    """Создаёт все таблицы, если их ещё нет"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных инициализирована")

async def get_session() -> AsyncSession:
    """Возвращает сессию для работы с БД"""
    async with async_session() as session:
        yield session