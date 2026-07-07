# Tutor Bot — Техническое решение (ТР)

## 1. Архитектура системы

[Telegram User] ↔ [Telegram API] ↔ [aiogram Bot] ↔ [PostgreSQL DB]
│
├── [JobQueue: напоминания]
└── [Async tasks: очистка]

**Компоненты:**

- **Python 3.11** + **aiogram 3.x** — асинхронный фреймворк для бота.
- **PostgreSQL 15** — основная база данных (через `asyncpg`).
- **Фоновые задачи** — встроенный `JobQueue` + отдельные `asyncio`-циклы.

## 2. Технологический стек

| Компонент      | Технология                       | Зачем                                   |
| -------------- | -------------------------------- | --------------------------------------- |
| Язык           | Python 3.11                      | Быстрая разработка, огромная экосистема |
| Фреймворк бота | aiogram 3.x                      | Асинхронный, FSM, JobQueue "из коробки" |
| ORM            | SQLAlchemy 2.0 (async) + asyncpg | Гибкость, типизация, поддержка async    |
| Миграции       | Alembic                          | Управление схемой БД                    |
| Логирование    | structlog                        | Структурированные логи для отладки      |
| Хостинг        | Railway / Amvera                 | Простой деплой, переменные окружения    |
| База данных    | PostgreSQL 15                    | Надёжность, индексы, транзакции         |

## 3. Схема базы данных

### 3.1. Таблица `users`

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    role VARCHAR(20) CHECK (role IN ('tutor', 'student')),
    registered_at TIMESTAMP DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb  -- часовой пояс, язык
);
```

### 3.2. Таблица `invites`

```sql
CREATE TABLE invites (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    tutor_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,  -- now + 7 days
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP
);

CREATE INDEX idx_invites_code ON invites(code);
CREATE INDEX idx_invites_expires ON invites(expires_at) WHERE is_used = FALSE;
```

### 3.3. Таблица `relationships`

```sql
CREATE TABLE relationships (
    id BIGSERIAL PRIMARY KEY,
    tutor_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) CHECK (status IN ('active', 'paused', 'inactive')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Защита от дублирования активной связи
CREATE UNIQUE INDEX idx_relationships_unique_active ON relationships(tutor_id, student_id) WHERE status = 'active';
```

### 3.4. Таблица `subscriptions` (абонементы)

```sql
CREATE TABLE subscriptions (
    id BIGSERIAL PRIMARY KEY,
    relationship_id BIGINT NOT NULL REFERENCES relationships(id) ON DELETE CASCADE,
    total_lessons INT NOT NULL CHECK (total_lessons > 0),
    used_lessons INT DEFAULT 0,
    price_per_lesson DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP  -- NULL = бессрочный
);
```

### 3.5. Таблица `lessons` (занятия)

```sql
CREATE TABLE lessons (
    id BIGSERIAL PRIMARY KEY,
    relationship_id BIGINT NOT NULL REFERENCES relationships(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    duration_minutes INT NOT NULL CHECK (duration_minutes BETWEEN 10 AND 180),
    subject VARCHAR(255),
    status VARCHAR(30) CHECK (status IN ('scheduled', 'completed', 'cancelled', 'missed', 'failed_to_notify')) DEFAULT 'scheduled',
    paid BOOLEAN DEFAULT TRUE,
    notified BOOLEAN DEFAULT FALSE,
    notify_attempts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lessons_start_time ON lessons(start_time);
CREATE INDEX idx_lessons_status ON lessons(status) WHERE status = 'scheduled';
CREATE INDEX idx_lessons_notified ON lessons(notified) WHERE notified = FALSE AND status = 'scheduled';
```

---

## 4. Контракты Telegram-команд

### 4.1. Общие команды

| Команда  | Роль | Описание                              |
| -------- | ---- | ------------------------------------- |
| `/start` | Все  | Регистрация / обработка invite-ссылки |
| `/help`  | Все  | Справка по командам                   |

### 4.2. Команды репетитора

| Команда         | Описание                   | FSM (состояния)                                                                     |
| --------------- | -------------------------- | ----------------------------------------------------------------------------------- |
| `/menu`         | Меню репетитора            | Нет                                                                                 |
| `/add_lesson`   | Добавить занятие           | `WaitingStudent`, `WaitingDate`, `WaitingTime`, `WaitingDuration`, `WaitingSubject` |
| `/my_lessons`   | Расписание                 | Нет                                                                                 |
| `/students`     | Список учеников            | Нет                                                                                 |
| `/student [ID]` | Управление учеником        | Нет (инлайн-кнопки)                                                                 |
| `/invite`       | Создать ссылку-приглашение | Нет                                                                                 |
| `/settings`     | Настройки                  | `WaitingTimezone`                                                                   |

### 4.3. Команды ученика

| Команда       | Описание    | FSM (состояния) |
| ------------- | ----------- | --------------- |
| `/my_lessons` | Мои занятия | Нет             |
| `/balance`    | Мой баланс  | Нет             |

---

## 5. Интеграции с внешними сервисами

### 5.1. Telegram Bot API

- **Библиотека:** `aiogram`
- **Токен:** через `@BotFather`
- **Методы:** `send_message`, `send_photo`, `edit_message_reply_markup`
- **Формат:** MarkdownV2 для форматирования

### 5.2. База данных

- **Драйвер:** `asyncpg`
- **Пулы:** min=5, max=20
- **Транзакции:** `async with async_session.begin():` для всех изменяющих операций

---

## 6. Фоновые задачи

### 6.1. Напоминания (каждую минуту)

```python
async def send_reminders():
    lessons = await db.fetch_all(
        "SELECT * FROM lessons WHERE start_time BETWEEN NOW() AND NOW() + INTERVAL '31 minutes' "
        "AND status = 'scheduled' AND notified = false"
    )
    for lesson in lessons:
        try:
            await bot.send_message(lesson.student_id, f"Напоминание: занятие через {remaining_minutes} минут")
            await db.execute("UPDATE lessons SET notified = true WHERE id = ?", lesson.id)
        except Exception as e:
            await db.execute("UPDATE lessons SET notify_attempts = notify_attempts + 1 WHERE id = ?", lesson.id)
            if lesson.notify_attempts >= 3:
                await db.execute("UPDATE lessons SET status = 'failed_to_notify' WHERE id = ?", lesson.id)
                await bot.send_message(tutor_id, f"Не удалось уведомить ученика о занятии {lesson.id}")
```

### 6.2. Автоматическое завершение занятий (раз в час)

```python
async def auto_complete_lessons():
    lessons = await db.fetch_all(
        "SELECT * FROM lessons WHERE status = 'scheduled' "
        "AND start_time + (duration_minutes * INTERVAL '1 minute') <= NOW() "
        "AND start_time + (duration_minutes * INTERVAL '1 minute') >= NOW() - INTERVAL '10 minutes'"
    )
    for lesson in lessons:
        await db.execute("UPDATE lessons SET status = 'missed' WHERE id = ?", lesson.id)
```

### 6.3. Очистка просроченных приглашений (раз в день)

```python
async def clean_expired_invites():
    await db.execute(
        "UPDATE invites SET is_used = true WHERE expires_at < NOW() AND is_used = false"
    )
```

---

## 7. Переменные окружения (`.env`)

```env
# Telegram
BOT_TOKEN=ваш_токен_от_botfather
TUTOR_TELEGRAM_ID=ваш_telegram_id

# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/tutor_bot
TEST_DATABASE_URL=sqlite+aiosqlite:///test.db

# Настройки
REMINDER_MINUTES=30
FREE_CANCELLATION_HOURS=3
MAX_NOTIFY_ATTEMPTS=3
INVITE_EXPIRE_DAYS=7
```

---

## 8. Структура проекта

```
tutor_bot/
├── main.py                     # Точка входа
├── config.py                   # Загрузка .env
├── db/
│   ├── models.py               # SQLAlchemy модели
│   ├── session.py              # Асинхронная сессия
│   └── migrations/             # Alembic миграции
├── handlers/
│   ├── common.py               # /start, /help
│   ├── tutor.py                # Команды репетитора
│   ├── student.py              # Команды ученика
│   └── admin.py                # (опционально)
├── keyboards/
│   ├── tutor.py                # Инлайн-клавиатуры репетитора
│   └── student.py              # Инлайн-клавиатуры ученика
├── services/
│   ├── lesson_service.py       # CRUD занятий
│   ├── subscription_service.py # Работа с абонементами
│   └── notification_service.py # Отправка уведомлений
├── tasks/
│   ├── reminders.py            # Напоминания
│   └── cleanup.py              # Очистка просроченных
└── docs/
    ├── bizreq.md               # Бизнес-требования
    └── tech.md                 # Техническое решение (этот файл)
```

---

## 9. Метрики и мониторинг (MVP)

- **Логирование:** `structlog` (INFO в консоль)
- **Ошибки:** Все исключения логируются с traceback
- **Ключевые метрики:**
  - количество успешно отправленных напоминаний
  - количество занятий в статусе `scheduled` / `missed`
