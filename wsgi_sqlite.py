from sqlite_web import app, initialize_app
import os

# ПРЯМОЙ ПУТЬ к файлу базы данных (НЕ URL!)
DB_PATH = '/data/tutor_bot.db'  # замените на имя вашего файла

# Проверяем, существует ли файл
if not os.path.exists(DB_PATH):
    print(f"⚠️ ВНИМАНИЕ: База данных не найдена по пути {DB_PATH}")
    # Если файла нет, создадим временный, чтобы избежать ошибки
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.close()
    print(f"✅ Создан пустой файл базы данных: {DB_PATH}")

# Инициализируем приложение
initialize_app(DB_PATH, read_only=True)

# Объект для Gunicorn
application = app