import asyncio
import uvicorn
from threading import Thread

from tutor_bot.main import main as bot_main
from tutor_bot.api.main import app


def run_bot():
    """Запуск Telegram бота в отдельном потоке"""
    asyncio.run(bot_main())


def run_api():
    """Запуск FastAPI"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Запускаем бота в потоке
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем API
    run_api()