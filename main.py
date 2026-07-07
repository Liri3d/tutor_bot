"""Telegram bot entrypoint.

This module is imported by tutor_bot/run.py.

It wires up aiogram Dispatcher and registers handlers from handlers/*.
"""

import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config

from .handlers import common as common_handlers
from .handlers import tutor as tutor_handlers
from .handlers import student as student_handlers


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start bot + register handlers."""
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    # Expose dp to handler modules that use @dp decorators
    # (tutor.py/student.py/common.py were written with global dp usage).
    tutor_handlers.dp = dp
    student_handlers.dp = dp
    common_handlers.dp = dp

    # Register handlers for /start and role selection
    dp.message.register(common_handlers.cmd_start)
    dp.callback_query.register(common_handlers.ask_role)  # no-op; kept for safety

    # role callbacks
    dp.callback_query.register(common_handlers.handle_role_tutor, lambda c: c.data == "role_tutor")
    dp.callback_query.register(common_handlers.handle_role_student, lambda c: c.data == "role_student")

    # Load other callback handlers (decorated in tutor.py/student.py)
    # No explicit registration needed if decorators were attached to dp correctly above.
    await dp.start_polling(bot)

