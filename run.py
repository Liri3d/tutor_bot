import asyncio
import uvicorn
from threading import Thread

from main import main as bot_main
from api.main import app

async def run_bot():
    await bot_main()


def run_api():
    """Запуск FastAPI"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Запускаем бота в главном потоке
    asyncio.create_task(run_bot())
    
    # Запускаем uvicorn (он тоже асинхронный)
    uvicorn.run(app, host="0.0.0.0", port=8000)