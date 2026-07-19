import os
import asyncio
import uvicorn
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ENVIRONMENT, init_bot_info
from handlers.common import common_router
from handlers.tutor import tutor_router
from services import SessionService
from api.main import app
import subprocess

logging.basicConfig(level=logging.INFO)

RUN_FRONTEND = os.getenv("RUN_FRONTEND", "true").lower() == "true"

async def run_bot():
    """Запуск бота"""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(common_router)
    dp.include_router(tutor_router)
    
    await SessionService.init_db()
    await init_bot_info()
    
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

async def run_api():
    """Запуск FastAPI"""
    env = ENVIRONMENT
    host = "0.0.0.0" if env == "production" else "localhost"
    port = int(os.getenv("PORT", 80))

    config = uvicorn.Config(app, host=host, port=port, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

# async def run_frontend():
#     """Запуск фронтенда в режиме разработки"""
#     if not RUN_FRONTEND:
#         print("⏭️ Запуск фронтенда пропущен (RUN_FRONTEND=false)")
#         return
    
#     frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    
#     if not os.path.exists(frontend_dir):
#         print("⚠️ Папка frontend не найдена")
#         return
    
#     print("🔧 Запуск фронтенда в режиме разработки...")
    
#     try:
#         # Запускаем npm run dev
#         process = await asyncio.create_subprocess_exec(
#             "npm", "run", "dev",
#             cwd=frontend_dir,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )
        
#         # Читаем вывод в фоне
#         async def read_output(pipe, name):
#             while True:
#                 line = await pipe.readline()
#                 if not line:
#                     break
#                 print(f"[Frontend] {line.decode().strip()}")
        
#         # Запускаем чтение вывода
#         await asyncio.gather(
#             read_output(process.stdout, "stdout"),
#             read_output(process.stderr, "stderr"),
#             return_exceptions=True
#         )
        
#         # Ждем завершения процесса (это не должно произойти)
#         await process.wait()
        
#     except FileNotFoundError:
#         print("❌ npm не найден. Убедитесь, что Node.js установлен.")
#     except Exception as e:
#         print(f"❌ Ошибка при запуске фронтенда: {e}")

async def main():
    await SessionService.init_db()
    
    # tasks = [
    #     run_bot(),
    #     run_api(),
    # ]

    # if ENVIRONMENT == "development" and RUN_FRONTEND:
    #     tasks.append(run_frontend())
    
    # await asyncio.gather(*tasks)

    await asyncio.gather(run_bot(), run_api())

if __name__ == "__main__":
    asyncio.run(main())