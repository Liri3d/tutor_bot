from __future__ import annotations

from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import Relationship, User
from keyboards import get_student_keyboard
from services import get_session, get_user_by_telegram
from services.lesson_service import get_student_lessons

router = Router()


async def _get_student(session: AsyncSession, telegram_id: int) -> User:
    user = await get_user_by_telegram(session, telegram_id)
    if not user or user.role != "student":
        raise ValueError("Вы не зарегистрированы как ученик")
    return user


async def show_student_menu(message: types.Message, user: User):
    """Показать главное меню ученика"""
    text = (
        f"👋 Привет, {user.first_name or 'ученик'}!\n\n"
        "Выберите действие с помощью кнопок ниже:"
    )
    await message.answer(text, reply_markup=get_student_keyboard())


@router.message(lambda msg: msg.text == "📅 Мои занятия")
async def handle_my_lessons(message: types.Message):
    """Обработка кнопки 'Мои занятия' для ученика"""
    telegram_id = message.from_user.id

    async for session in get_session():
        try:
            student = await _get_student(session, telegram_id)
            lessons = await get_student_lessons(session=session, student_id=student.id, limit=20)

            if not lessons:
                await message.answer("У вас пока нет запланированных занятий.")
                return

            lines: list[str] = ["Ваши занятия:"]
            for l in lessons:
                subj = f" — {l.subject}" if l.subject else ""
                lines.append(
                    f"• {l.start_time:%Y-%m-%d %H:%M} ({l.duration_minutes} мин){subj}"
                )

            await message.answer("\n".join(lines))
        except Exception as e:
            await message.answer(f"❌ {e}")


@router.message(lambda msg: msg.text == "💰 Мой баланс")
async def handle_my_balance(message: types.Message):
    """Обработка кнопки 'Мой баланс'"""
    # В текущем каркасе нет сервиса/CRUD-методов для вычисления баланса подписок.
    # Чтобы не сломать архитектуру и не добавлять лишнюю логику, показываем понятное сообщение.
    await message.answer(
        "💰 Баланс пока в разработке.\n"
        "В БД есть Subscription, но в сервисном слое пока нет расчёта/вывода баланса."
    )


@router.message(lambda msg: msg.text == "👤 Мой репетитор")
async def handle_my_tutor(message: types.Message):
    """Обработка кнопки 'Мой репетитор'"""
    telegram_id = message.from_user.id

    async for session in get_session():
        try:
            student = await _get_student(session, telegram_id)

            stmt = (
                select(User)
                .join(Relationship, Relationship.tutor_id == User.id)
                .where(
                    Relationship.student_id == student.id,
                    Relationship.status == "active",
                )
            )
            result = await session.execute(stmt)
            tutor = result.scalar_one_or_none()

            if not tutor:
                await message.answer("У вас пока нет активного репетитора.")
                return

            await message.answer(
                f"👤 Ваш репетитор: {tutor.first_name or 'репетитор'}"
                + (f" (tg: {tutor.telegram_id})" if tutor.telegram_id else "")
            )
        except Exception as e:
            await message.answer(f"❌ {e}")

