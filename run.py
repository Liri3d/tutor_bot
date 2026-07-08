import asyncio
import uvicorn
from threading import Thread

from main import main as bot_main
from api.main import app

def run_api():
    """Запуск FastAPI"""
    uvicorn.run(app, host="localhost", port=8000)

async def run_bot():
    """Запуск бота"""
    await bot_main()

async def main():
    """Главная асинхронная функция"""
    # Запускаем бота в фоне
    bot_task = asyncio.create_task(run_bot())
    
    # Запускаем uvicorn сервер (он блокирующий, но асинхронный)
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    
    # Ждём выполнения обоих задач
    await asyncio.gather(bot_task, server.serve())

if __name__ == "__main__":
    asyncio.run(main())