"""Telegram bot entrypoint."""

import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import config
from db import init_db, close_db
from handlers.common import cmd_start, handle_role_tutor, handle_role_student
from handlers.tutor import router as tutor_router
from handlers.student import router as student_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start bot + register handlers."""
    # Инициализация БД
    await init_db()
    
    # Создаем бота с новым синтаксисом
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем команду /start
    dp.message.register(cmd_start)
    
    # Регистрируем callback'и для выбора роли
    dp.callback_query.register(handle_role_tutor, lambda c: c.data == "role_tutor")
    dp.callback_query.register(handle_role_student, lambda c: c.data == "role_student")

    # Подключаем роутеры
    dp.include_router(tutor_router)
    dp.include_router(student_router)

    logger.info("🚀 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())