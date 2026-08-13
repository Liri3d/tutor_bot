import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if not BOT_TOKEN:
    raise ValueError("Токен не найден!")

BOT_ID = None
BOT_USERNAME = None

async def init_bot_info():
    """Получить информацию о боте при запуске"""
    from aiogram import Bot
    
    global BOT_ID, BOT_USERNAME
    
    if BOT_ID and BOT_USERNAME:
        print(f"ℹ️ Информация о боте уже загружена: @{BOT_USERNAME}")
        return
    
    bot = Bot(token=BOT_TOKEN)
    try:
        me = await bot.get_me()
        BOT_USERNAME = me.username
        BOT_ID = me.id
        print(f"✅ Бот найден: @{BOT_USERNAME} (id: {BOT_ID})")
    except Exception as e:
        print(f"❌ Не удалось получить информацию о боте: {e}")
        try:
            BOT_ID = int(BOT_TOKEN.split(':')[0])
            print(f"⚠️ Использован ID из токена: {BOT_ID}")
        except:
            pass
    finally:
        await bot.session.close()