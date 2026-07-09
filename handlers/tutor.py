from __future__ import annotations

from datetime import datetime

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Relationship, User
from keyboards import get_tutor_keyboard
from services import get_session, get_user_by_telegram
from services.lesson_service import create_new_lesson, get_student_lessons
from services.relationship_service import create_invite_code
from services.user_service import delete_tutor_account

from aiogram.fsm.state import State, StatesGroup

router = Router()

@router.message(lambda msg: msg.text == "🗑️ Удалить аккаунт")
async def handle_delete_account(message: types.Message, state: FSMContext):
    """Запуск процесса удаления аккаунта"""
    await message.answer("🔴 КНОПКА СРАБОТАЛА!")

async def show_tutor_menu(message: types.Message, user: User):
    """Показать главное меню репетитора"""
    text = (
        f"👋 Здравствуйте, {user.first_name or 'репетитор'}!\n\n"
        "Выберите действие с помощью кнопок ниже:"
    )

    await message.answer(text, reply_markup=get_tutor_keyboard())


async def _get_tutor(session: AsyncSession, telegram_id: int) -> User:
    user = await get_user_by_telegram(session, telegram_id)
    if not user or user.role != "tutor":
        raise ValueError("Вы не зарегистрированы как репетитор")
    return user


@router.message(lambda msg: msg.text == "📅 Мои занятия")
async def handle_my_lessons(message: types.Message):
    """Обработка кнопки 'Мои занятия' для репетитора"""
    telegram_id = message.from_user.id

    async for session in get_session():
        try:
            tutor = await _get_tutor(session, telegram_id)

            # Список занятий репетитора = занятия всех активных relationships репетитора
            stmt = (
                select(User)
            )
            # В текущем каркасе нет CRUD/сервиса для "занятий репетитора" напрямую.
            # Поэтому реализуем минимальный рабочий вывод: получаем active relationships
            # через relationship table и затем берём занятия студентов через get_student_lessons.
            rel_stmt = (
                select(Relationship)
                .where(Relationship.tutor_id == tutor.id)
                .where(Relationship.status == "active")
            )
            rel_res = await session.execute(rel_stmt)
            relationships = list(rel_res.scalars().all())

            if not relationships:
                await message.answer("У вас пока нет активных учеников.")
                return

            all_lines: list[str] = []
            # ограничим по времени/кол-ву через get_student_lessons
            for rel in relationships:
                lessons = await get_student_lessons(session=session, student_id=rel.student_id, limit=5)
                for l in lessons:
                    subj = f" — {l.subject}" if l.subject else ""
                    all_lines.append(
                        f"• {l.start_time:%Y-%m-%d %H:%M} (ученик: {rel.student_id}) ({l.duration_minutes} мин){subj}"
                    )

            if not all_lines:
                await message.answer("На ближайшее время занятий пока нет.")
                return

            # простая сортировка по строкам неудобна; делаем сортировку по start_time через повторный сбор не усложняя.
            all_lines = sorted(all_lines)
            await message.answer("Ближайшие занятия:\n" + "\n".join(all_lines[:20]))
        except Exception as e:
            await message.answer(f"❌ {e}")


@router.message(lambda msg: msg.text == "👥 Мои ученики")
async def handle_my_students(message: types.Message):
    """Обработка кнопки 'Мои ученики'"""
    telegram_id = message.from_user.id

    async for session in get_session():
        try:
            tutor = await _get_tutor(session, telegram_id)
            stmt = (
                select(User)
                .join(Relationship, Relationship.student_id == User.id)
                .where(Relationship.tutor_id == tutor.id)
                .where(Relationship.status == "active")
            )
            res = await session.execute(stmt)
            students = res.scalars().all()

            if not students:
                await message.answer("У вас пока нет активных учеников.")
                return

            lines = ["Ваши ученики:"]
            for s in students:
                lines.append(f"• {s.first_name or 'ученик'} (tg: {s.telegram_id})")

            await message.answer("\n".join(lines))
        except Exception as e:
            await message.answer(f"❌ {e}")


@router.message(lambda msg: msg.text == "🔗 Пригласить ученика")
async def handle_invite(message: types.Message):
    """Обработка кнопки 'Пригласить ученика'"""
    telegram_id = message.from_user.id

    async for session in get_session():
        try:
            tutor = await _get_tutor(session, telegram_id)
            code = await create_invite_code(session=session, tutor_id=tutor.id)
            await message.answer(
                "🔗 Ваш код приглашения:\n"
                f"invite_{code}\n\n"
                "Отправьте код ученику (откройте ссылку/укажите код в /start)."
            )
        except Exception as e:
            await message.answer(f"❌ {e}")


class AddLessonStates(StatesGroup):
    waiting_for_student_id = State()
    waiting_for_start_time = State()
    waiting_for_duration = State()
    waiting_for_subject = State()
    waiting_for_paid = State()


@router.message(lambda msg: msg.text == "➕ Добавить занятие")
async def handle_add_lesson(message: types.Message, state: FSMContext):
    """Обработка кнопки 'Добавить занятие' (FSM)"""
    telegram_id = message.from_user.id
    await state.clear()

    async for session in get_session():
        try:
            tutor = await _get_tutor(session, telegram_id)

            rel_stmt = (
                select(Relationship)
                .where(Relationship.tutor_id == tutor.id)
                .where(Relationship.status == "active")
            )
            rel_res = await session.execute(rel_stmt)
            relationships = list(rel_res.scalars().all())

            if not relationships:
                await message.answer("Сначала подключите ученика через '🔗 Пригласить ученика'.")
                return

            # Кнопки: по student_id (минимальный вариант без доп. клавиатурных сущностей)
            keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=f"{rel.student_id}") for rel in relationships[:8]]],
                resize_keyboard=True,
                one_time_keyboard=True,
            )

            await state.update_data(tutor_id=tutor.id)
            await state.set_state(AddLessonStates.waiting_for_student_id)

            await message.answer(
                "Выберите ученка (tg user id) из кнопок ниже или введите id текстом:\n"
                "Отмена: нажмите кнопку меню '⚙️ Настройки' или '📅 Мои занятия'.",
                reply_markup=keyboard,
            )
        except Exception as e:
            await message.answer(f"❌ {e}")


@router.message(AddLessonStates.waiting_for_student_id)
async def fsm_student_id(message: types.Message, state: FSMContext):
    telegram_id_text = message.text.strip()
    if not telegram_id_text.isdigit():
        await message.answer("Введите числовой ID ученика.")
        return

    await state.update_data(student_id=int(telegram_id_text))
    await state.set_state(AddLessonStates.waiting_for_start_time)
    await message.answer("Введите дату и время начала в формате: YYYY-MM-DD HH:MM")


@router.message(AddLessonStates.waiting_for_start_time)
async def fsm_start_time(message: types.Message, state: FSMContext):
    text = message.text.strip()
    try:
        dt = datetime.strptime(text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("Неверный формат. Пример: 2026-07-10 18:30")
        return

    await state.update_data(start_time=dt)
    await state.set_state(AddLessonStates.waiting_for_duration)
    await message.answer("Введите длительность в минутах (10..180)")


@router.message(AddLessonStates.waiting_for_duration)
async def fsm_duration(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("Введите число минут.")
        return

    duration = int(text)
    if duration < 10 or duration > 180:
        await message.answer("Длительность должна быть в диапазоне 10..180 минут.")
        return

    await state.update_data(duration_minutes=duration)
    await state.set_state(AddLessonStates.waiting_for_subject)
    await message.answer("Введите предмет (или отправьте '-' чтобы пропустить)")


@router.message(AddLessonStates.waiting_for_subject)
async def fsm_subject(message: types.Message, state: FSMContext):
    subj = message.text.strip()
    if subj == "-":
        subj = None

    await state.update_data(subject=subj)
    await state.set_state(AddLessonStates.waiting_for_paid)
    await message.answer("Оплачено? Ответьте: да/нет")


@router.message(AddLessonStates.waiting_for_paid)
async def fsm_paid(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    if text in {"да", "yes", "y", "1"}:
        paid = True
    elif text in {"нет", "no", "n", "0"}:
        paid = False
    else:
        await message.answer("Ответьте 'да' или 'нет'.")
        return

    data = await state.get_data()
    tutor_id = data["tutor_id"]
    student_id = data["student_id"]
    start_time = data["start_time"]
    duration_minutes = data["duration_minutes"]
    subject = data.get("subject")

    await state.clear()

    async for session in get_session():
        try:
            # relationship_id можно получить через relationship table
            rel_stmt = (
                select(Relationship.id)
                .where(Relationship.tutor_id == tutor_id)
                .where(Relationship.student_id == student_id)
                .where(Relationship.status == "active")
            )
            rel_res = await session.execute(rel_stmt)
            relationship_id = rel_res.scalar_one_or_none()
            if not relationship_id:
                await message.answer("Не найдена активная связь репетитор-ученик.")
                return

            await create_new_lesson(
                session=session,
                relationship_id=relationship_id,
                start_time=start_time,
                duration_minutes=duration_minutes,
                subject=subject,
                paid=paid,
            )

            await message.answer("✅ Занятие добавлено.")
        except Exception as e:
            await message.answer(f"❌ Не удалось добавить занятие: {e}")


@router.message(lambda msg: msg.text == "⚙️ Настройки")
async def handle_settings(message: types.Message):
    """Обработка кнопки 'Настройки' (минимум, не ломающий архитектуру)"""
    await message.answer(
        "⚙️ Настройки пока не реализованы в полном объёме.\n\n"
        "Доступно: добавление занятия и управление учениками/инвайтами."
    )

class DeleteAccountStates(StatesGroup):
    waiting_for_confirmation = State()

@router.message(lambda msg: msg.text == "🗑️ Удалить аккаунт")
async def handle_delete_account(message: types.Message, state: FSMContext):
    """Запуск процесса удаления аккаунта"""
    telegram_id = message.from_user.id
    
    async for session in get_session():
        try:
            tutor = await _get_tutor(session, telegram_id)
            
            import secrets
            code = secrets.token_hex(4).upper()
            await state.update_data(confirmation_code=code, tutor_id=tutor.id)
            
            await state.set_state(DeleteAccountStates.waiting_for_confirmation)

            # ✅ Убираем клавиатуру
            from keyboards import remove_keyboard
            
            await message.answer(
                f"⚠️ **ВНИМАНИЕ!**\n\n"
                f"Вы собираетесь удалить свой аккаунт репетитора.\n\n"
                f"Это действие **НЕОБРАТИМО**. Будут удалены:\n"
                f"• Все ваши ученики\n"
                f"• Все занятия\n"
                f"• Все приглашения\n"
                f"• Вся информация о вас\n\n"
                f"Для подтверждения отправьте код:\n"
                f"`УДАЛИТЬ АККАУНТ {code}`\n\n"
                f"(Введите этот код в точности, включая пробелы)",
                parse_mode="Markdown",
                reply_markup=remove_keyboard()  # ← Убираем кнопки!
            )
        except Exception as e:
            await message.answer(f"❌ {e}")
     
@router.message(DeleteAccountStates.waiting_for_confirmation)
async def catch_all_in_delete_state(message: types.Message, state: FSMContext):
    """
    Ловит все сообщения, пока пользователь в состоянии удаления аккаунта.
    Если это не код подтверждения — напоминает, что нужно ввести код.
    """
    # Проверяем, является ли сообщение кодом подтверждения
    data = await state.get_data()
    expected_code = f"УДАЛИТЬ АККАУНТ {data.get('confirmation_code')}"
    user_input = message.text.strip()
    
    if user_input == expected_code:
        # ✅ Код верный — вызываем удаление
        await confirm_delete_account(message, state)
    else:
        # ❌ Неверный код — напоминаем
        await message.answer(
            f"⚠️ Для удаления аккаунта введите точный код.\n"
            f"Ожидается: `{expected_code}`\n\n"
            f"Если вы передумали, просто нажмите /start",
            parse_mode="Markdown"
        )

async def confirm_delete_account(message: types.Message, state: FSMContext):
    """Подтверждение удаления аккаунта"""
    data = await state.get_data()
    expected_code = f"УДАЛИТЬ АККАУНТ {data.get('confirmation_code')}"
    user_input = message.text.strip()
    
    if user_input != expected_code:
        await message.answer(
            f"❌ Неверный код.\n\n"
            f"Ожидается: `{expected_code}`\n"
            f"Вы ввели: `{user_input}`",
            parse_mode="Markdown"
        )
        return
    
    # Код верный — удаляем
    telegram_id = message.from_user.id
    
    async for session in get_session():
        try:
            # Вызываем сервис для удаления
            await delete_tutor_account(
                session=session,
                telegram_id=telegram_id,
                confirmation_code=user_input
            )
            await session.commit()
            
            await state.clear()
            
            from keyboards import remove_keyboard
            await message.answer(
                "✅ Ваш аккаунт и все связанные данные были успешно удалены.\n\n"
                "Если вы захотите вернуться, просто нажмите /start и зарегистрируйтесь заново.",
                reply_markup=remove_keyboard()
            )
        except Exception as e:
            await session.rollback()
            await message.answer(f"❌ Ошибка при удалении: {e}")
            await state.clear()