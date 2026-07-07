import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import sessionmaker
from .models import Base

# Читаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/tutor_bot"
)

# Создаём асинхронный движок
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,  # В продакшене выключить, для отладки можно включить
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
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
        # Создаём все таблицы
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных инициализирована")


async def close_db() -> None:
    """Закрытие соединения с базой данных"""
    await engine.dispose()
    print("✅ Соединение с БД закрыто")