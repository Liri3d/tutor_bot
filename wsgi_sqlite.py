from sqlite_web import app, initialize_app
import os 

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tutor_bot.db")

# Здесь укажите ПУТЬ к вашему файлу БД в постоянном хранилище Amvera
# Папка для данных на Amvera - /data [citation:9]
initialize_app(DATABASE_URL, read_only=True)

# Объект 'app' и будет использован Gunicorn
application = app