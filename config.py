import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Класс для хранения всех настроек"""
    
    # Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    TUTOR_TELEGRAM_ID: int = int(os.getenv("TUTOR_TELEGRAM_ID", 0))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/tutor_bot"
    )
    
    # Настройки
    REMINDER_MINUTES: int = int(os.getenv("REMINDER_MINUTES", 30))
    FREE_CANCELLATION_HOURS: int = int(os.getenv("FREE_CANCELLATION_HOURS", 3))
    MAX_NOTIFY_ATTEMPTS: int = int(os.getenv("MAX_NOTIFY_ATTEMPTS", 3))
    INVITE_EXPIRE_DAYS: int = int(os.getenv("INVITE_EXPIRE_DAYS", 7))
    
    @classmethod
    def validate(cls) -> None:
        """Проверка обязательных настроек"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в .env файле!")
        if cls.TUTOR_TELEGRAM_ID == 0:
            raise ValueError("TUTOR_TELEGRAM_ID не найден в .env файле!")


# Создаём экземпляр конфига
config = Config()