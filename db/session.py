import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from .models import Base

# Читаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./tutor_bot.db"
)

# Настройки для разных БД
is_sqlite = DATABASE_URL.startswith("sqlite")

# Базовые параметры подключения
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

# Для SQLite свои настройки
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Для PostgreSQL добавляем пул соединений
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 3600,
    })

# Создаём асинхронный движок
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    **engine_kwargs
)

# Создаём фабрику сессий
async_session_maker: async_sessionmaker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессий для Dependency Injection"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Инициализация базы данных - создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных инициализирована")


async def close_db() -> None:
    """Закрытие соединения с базой данных"""
    await engine.dispose()
    print("✅ Соединение с БД закрыто")