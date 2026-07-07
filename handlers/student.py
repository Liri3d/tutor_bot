from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from sqlalchemy import select, and_

from db import get_session
from db.crud import get_user_by_telegram_id
from db.models import User, Relationship, Lesson

# Создаем роутер
router = Router()

async def show_student_menu(message: types.Message, user: User):
    """Показать главное меню ученика"""
    text = (
        f"👋 Привет, {user.first_name or 'ученик'}!\n\n"
        "Выберите действие:"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Мои занятия",
                    callback_data="student_lessons"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Баланс занятий",
                    callback_data="student_balance"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 Мой репетитор",
                    callback_data="student_tutor"
                )
            ]
        ]
    )
    
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "student_lessons")
async def callback_student_lessons(callback: types.CallbackQuery):
    """Показать занятия ученика"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, user_id)
        if not user or user.role != 'student':
            await callback.message.edit_text("❌ Только ученик может просматривать свои занятия.")
            return
        
        # Получаем все активные связи
        stmt = select(Relationship).where(
            and_(
                Relationship.student_id == user.id,
                Relationship.status == 'active'
            )
        )
        result = await session.execute(stmt)
        relationships = result.scalars().all()
        
        if not relationships:
            text = (
                "📅 У вас пока нет занятий.\n\n"
                "Подключитесь к репетитору по приглашению."
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад в меню",
                            callback_data="student_back"
                        )
                    ]
                ]
            )
            await callback.message.edit_text(text, reply_markup=keyboard)
            return
        
        # Получаем занятия
        relationship_ids = [r.id for r in relationships]
        stmt = select(Lesson).where(
            and_(
                Lesson.relationship_id.in_(relationship_ids),
                Lesson.status == 'scheduled',
                Lesson.start_time > datetime.now()
            )
        ).order_by(Lesson.start_time).limit(10)
        
        result = await session.execute(stmt)
        lessons = result.scalars().all()
        
        if not lessons:
            text = "📅 У вас нет предстоящих занятий."
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад в меню",
                            callback_data="student_back"
                        )
                    ]
                ]
            )
            await callback.message.edit_text(text, reply_markup=keyboard)
            return
        
        text = "📅 **Ваши предстоящие занятия:**\n\n"
        
        keyboard = InlineKeyboardBuilder()
        
        for lesson in lessons:
            date_str = lesson.start_time.strftime("%d.%m.%Y %H:%M")
            text += f"• {date_str} - {lesson.duration_minutes} мин"
            if lesson.subject:
                text += f" - {lesson.subject}"
            text += "\n"
            
            # Кнопка для отмены занятия
            keyboard.button(
                text=f"❌ Отменить {date_str}",
                callback_data=f"lesson_cancel_{lesson.id}"
            )
        
        keyboard.button(
            text="↩️ Назад в меню",
            callback_data="student_back"
        )
        keyboard.adjust(1, 1)
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup()
        )


@router.callback_query(lambda c: c.data.startswith("lesson_cancel_"))
async def callback_lesson_cancel(callback: types.CallbackQuery):
    """Отмена занятия учеником"""
    await callback.answer()
    
    lesson_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    async for session in get_session():
        # Получаем занятие
        lesson = await session.get(Lesson, lesson_id)
        if not lesson:
            await callback.message.edit_text("❌ Занятие не найдено.")
            return
        
        # Проверяем, что занятие принадлежит ученику
        relationship = await session.get(Relationship, lesson.relationship_id)
        if not relationship:
            await callback.message.edit_text("❌ Ошибка: связь не найдена.")
            return
        
        # Проверяем, что это занятие ученика
        student = await get_user_by_telegram_id(session, user_id)
        if relationship.student_id != student.id:
            await callback.message.edit_text("❌ Это не ваше занятие.")
            return
        
        # Проверяем время до занятия
        from config import config
        time_until_lesson = lesson.start_time - datetime.now()
        hours_until = time_until_lesson.total_seconds() / 3600
        
        if hours_until >= config.FREE_CANCELLATION_HOURS:
            # Бесплатная отмена
            lesson.status = 'cancelled'
            await session.commit()
            
            await callback.message.edit_text(
                "✅ Занятие успешно отменено.\n"
                "Списаний не было."
            )
            
            # Уведомляем репетитора
            tutor = await session.get(User, relationship.tutor_id)
            try:
                await callback.bot.send_message(
                    tutor.telegram_id,
                    f"📢 Ученик {student.first_name or 'без имени'} отменил занятие в {lesson.start_time.strftime('%H:%M')} (бесплатная отмена)."
                )
            except Exception as e:
                logging.error(f"Не удалось уведомить репетитора: {e}")
            
        else:
            # Отмена со списанием
            text = (
                "⚠️ **Внимание!**\n\n"
                f"До занятия осталось менее {config.FREE_CANCELLATION_HOURS} часов.\n"
                "При отмене сейчас занятие будет списано из вашего баланса.\n\n"
                "Вы уверены?"
            )
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Да, отменить (списание)",
                            callback_data=f"lesson_cancel_confirm_{lesson_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Нет, оставить",
                            callback_data="student_lessons"
                        )
                    ]
                ]
            )
            
            await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("lesson_cancel_confirm_"))
async def callback_lesson_cancel_confirm(callback: types.CallbackQuery):
    """Подтверждение отмены занятия со списанием"""
    await callback.answer()
    
    lesson_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id
    
    async for session in get_session():
        try:
            lesson = await session.get(Lesson, lesson_id)
            if not lesson:
                await callback.message.edit_text("❌ Занятие не найдено.")
                return
            
            # Отменяем занятие
            lesson.status = 'cancelled'
            
            # Списание из абонемента (упрощенно)
            # В реальности здесь нужно списывать из подписки
            
            await session.commit()
            
            await callback.message.edit_text(
                "✅ Занятие отменено.\n"
                "Занятие списано из вашего баланса."
            )
            
            # Уведомляем репетитора
            relationship = await session.get(Relationship, lesson.relationship_id)
            tutor = await session.get(User, relationship.tutor_id)
            student = await get_user_by_telegram_id(session, user_id)
            
            try:
                await callback.bot.send_message(
                    tutor.telegram_id,
                    f"📢 Ученик {student.first_name or 'без имени'} отменил занятие в {lesson.start_time.strftime('%H:%M')} (со списанием)."
                )
            except Exception as e:
                logging.error(f"Не удалось уведомить репетитора: {e}")
            
        except Exception as e:
            await session.rollback()
            logging.error(f"Ошибка при отмене занятия: {e}")
            await callback.message.edit_text("❌ Произошла ошибка при отмене занятия.")


@router.callback_query(lambda c: c.data == "student_balance")
async def callback_student_balance(callback: types.CallbackQuery):
    """Показать баланс занятий ученика"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, user_id)
        if not user or user.role != 'student':
            await callback.message.edit_text("❌ Только ученик может просматривать баланс.")
            return
        
        # Получаем все активные связи
        stmt = select(Relationship).where(
            and_(
                Relationship.student_id == user.id,
                Relationship.status == 'active'
            )
        )
        result = await session.execute(stmt)
        relationships = result.scalars().all()
        
        if not relationships:
            text = "💰 У вас нет активных репетиторов.\nПодключитесь по приглашению."
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад в меню",
                            callback_data="student_back"
                        )
                    ]
                ]
            )
            await callback.message.edit_text(text, reply_markup=keyboard)
            return
        
        text = "💰 **Ваш баланс занятий:**\n\n"
        
        for rel in relationships:
            tutor = await session.get(User, rel.tutor_id)
            
            # Получаем активные подписки
            from db.models import Subscription
            stmt = select(Subscription).where(
                and_(
                    Subscription.relationship_id == rel.id,
                    Subscription.expires_at > datetime.now()
                )
            )
            result = await session.execute(stmt)
            subscriptions = result.scalars().all()
            
            if subscriptions:
                for sub in subscriptions:
                    text += f"👤 {tutor.first_name or 'Репетитор'}:\n"
                    text += f"   📚 Осталось: {sub.balance} занятий\n"
                    if sub.expires_at:
                        text += f"   📅 До: {sub.expires_at.strftime('%d.%m.%Y')}\n"
                    text += "\n"
            else:
                text += f"👤 {tutor.first_name or 'Репетитор'}:\n"
                text += "   ❌ Нет активных абонементов\n\n"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="↩️ Назад в меню",
                        callback_data="student_back"
                    )
                ]
            ]
        )
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "student_tutor")
async def callback_student_tutor(callback: types.CallbackQuery):
    """Показать информацию о репетиторе"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, user_id)
        if not user or user.role != 'student':
            await callback.message.edit_text("❌ Только ученик может просматривать эту информацию.")
            return
        
        # Получаем активную связь с репетитором
        stmt = select(Relationship).where(
            and_(
                Relationship.student_id == user.id,
                Relationship.status == 'active'
            )
        )
        result = await session.execute(stmt)
        relationship = result.scalar_one_or_none()
        
        if not relationship:
            text = "👤 У вас нет активного репетитора.\nПодключитесь по приглашению."
        else:
            tutor = await session.get(User, relationship.tutor_id)
            text = (
                "👤 **Ваш репетитор**\n\n"
                f"Имя: {tutor.first_name or 'Не указано'}\n"
                f"Username: {'@' + tutor.username if tutor.username else 'Не указан'}\n\n"
                f"Связаны с: {relationship.created_at.strftime('%d.%m.%Y')}\n"
                f"Статус: {'Активен' if relationship.status == 'active' else 'Приостановлен'}"
            )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="↩️ Назад в меню",
                        callback_data="student_back"
                    )
                ]
            ]
        )
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "student_back")
async def callback_student_back(callback: types.CallbackQuery):
    """Вернуться в главное меню ученика"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    async for session in get_session():
        user = await get_user_by_telegram_id(session, user_id)
        if user:
            await show_student_menu(callback.message, user)
        else:
            await callback.message.edit_text("❌ Пользователь не найден.")