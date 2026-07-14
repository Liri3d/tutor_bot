# services/notification_service.py

import logging
from datetime import datetime
from typing import Optional
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.models import User


class NotificationService:
    """Сервис для отправки уведомлений"""

    @staticmethod
    async def notify_tutor_about_new_student(
        bot: Bot,
        tutor_telegram_id: int,
        student_first_name: str,
        student_username: Optional[str] = None
    ) -> bool:
        """
        Отправить уведомление репетитору о новом ученике.
        
        Args:
            bot: Экземпляр бота
            tutor_telegram_id: Telegram ID репетитора
            student_first_name: Имя ученика
            student_username: Username ученика (опционально)
        
        Returns:
            bool: True, если уведомление отправлено успешно
        """
        text = f"🎉 **К вам подключился новый ученик!**\n\n"
        text += f"👤 {student_first_name or 'Без имени'}"
        
        if student_username:
            text += f" (@{student_username})"
        
        try:
            await bot.send_message(tutor_telegram_id, text, parse_mode="Markdown")
            logging.info(f"✅ Уведомление отправлено репетитору {tutor_telegram_id}")
            return True
        except Exception as e:
            logging.error(f"❌ Не удалось уведомить репетитора {tutor_telegram_id}: {e}")
            return False

    # @staticmethod
    # async def notify_student_about_new_lesson(
    #     bot: Bot,
    #     student_telegram_id: int,
    #     lesson: Lesson,
    #     tutor_name: str
    # ) -> bool:
    #     """
    #     Отправить уведомление ученику о новом занятии.
        
    #     Args:
    #         bot: Экземпляр бота
    #         student_telegram_id: Telegram ID ученика
    #         lesson: Объект занятия
    #         tutor_name: Имя репетитора
        
    #     Returns:
    #         bool: True, если уведомление отправлено успешно
    #     """
    #     date_str = lesson.start_time.strftime("%d.%m.%Y")
    #     time_str = lesson.start_time.strftime("%H:%M")
    #     duration = lesson.duration_minutes
        
    #     text = (
    #         f"📚 **Новое занятие!**\n\n"
    #         f"👨‍🏫 Репетитор: {tutor_name or 'Репетитор'}\n"
    #         f"📅 Дата: {date_str}\n"
    #         f"⏰ Время: {time_str}\n"
    #         f"⏱ Длительность: {duration} мин"
    #     )
        
    #     if lesson.subject:
    #         text += f"\n📖 Предмет: {lesson.subject}"
        
    #     if not lesson.paid:
    #         text += "\n\n⚠️ **Внимание!** Занятие не оплачено.\n"
    #         text += "Свяжитесь с репетитором для оплаты."
        
    #     try:
    #         await bot.send_message(student_telegram_id, text, parse_mode="Markdown")
    #         logging.info(f"✅ Уведомление о занятии отправлено ученику {student_telegram_id}")
    #         return True
    #     except Exception as e:
    #         logging.error(f"❌ Не удалось уведомить ученика {student_telegram_id}: {e}")
    #         return False

    # @staticmethod
    # async def notify_lesson_reminder(
    #     bot: Bot,
    #     student_telegram_id: int,
    #     lesson: Lesson,
    #     tutor_name: str,
    #     minutes_before: int = 30
    # ) -> bool:
    #     """
    #     Отправить напоминание о занятии.
        
    #     Args:
    #         bot: Экземпляр бота
    #         student_telegram_id: Telegram ID ученика
    #         lesson: Объект занятия
    #         tutor_name: Имя репетитора
    #         minutes_before: За сколько минут напомнить
        
    #     Returns:
    #         bool: True, если уведомление отправлено успешно
    #     """
    #     time_str = lesson.start_time.strftime("%H:%M")
        
    #     text = (
    #         f"⏰ **Напоминание о занятии!**\n\n"
    #         f"👨‍🏫 Репетитор: {tutor_name or 'Репетитор'}\n"
    #         f"⏰ Занятие через {minutes_before} минут\n"
    #         f"🕐 Начало в {time_str}"
    #     )
        
    #     if lesson.subject:
    #         text += f"\n📖 {lesson.subject}"
        
    #     keyboard = InlineKeyboardMarkup(
    #         inline_keyboard=[
    #             [
    #                 InlineKeyboardButton(
    #                     text="❌ Отменить занятие",
    #                     callback_data=f"cancel_lesson_{lesson.id}"
    #                 )
    #             ]
    #         ]
    #     )
        
    #     try:
    #         await bot.send_message(
    #             student_telegram_id,
    #             text,
    #             parse_mode="Markdown",
    #             reply_markup=keyboard
    #         )
    #         logging.info(f"✅ Напоминание отправлено ученику {student_telegram_id}")
    #         return True
    #     except Exception as e:
    #         logging.error(f"❌ Не удалось отправить напоминание ученику {student_telegram_id}: {e}")
    #         return False

    # @staticmethod
    # async def notify_lesson_cancelled(
    #     bot: Bot,
    #     student_telegram_id: int,
    #     lesson: Lesson,
    #     tutor_name: str
    # ) -> bool:
    #     """
    #     Уведомить ученика об отмене занятия.
        
    #     Args:
    #         bot: Экземпляр бота
    #         student_telegram_id: Telegram ID ученика
    #         lesson: Объект занятия
    #         tutor_name: Имя репетитора
        
    #     Returns:
    #         bool: True, если уведомление отправлено успешно
    #     """
    #     date_str = lesson.start_time.strftime("%d.%m.%Y")
    #     time_str = lesson.start_time.strftime("%H:%M")
        
    #     text = (
    #         f"❌ **Занятие отменено!**\n\n"
    #         f"👨‍🏫 Репетитор: {tutor_name or 'Репетитор'}\n"
    #         f"📅 Дата: {date_str}\n"
    #         f"⏰ Время: {time_str}"
    #     )
        
    #     if lesson.subject:
    #         text += f"\n📖 {lesson.subject}"
        
    #     try:
    #         await bot.send_message(student_telegram_id, text, parse_mode="Markdown")
    #         logging.info(f"✅ Уведомление об отмене отправлено ученику {student_telegram_id}")
    #         return True
    #     except Exception as e:
    #         logging.error(f"❌ Не удалось уведомить ученика об отмене {student_telegram_id}: {e}")
    #         return False

    # @staticmethod
    # async def notify_tutor_about_cancellation(
    #     bot: Bot,
    #     tutor_telegram_id: int,
    #     student_name: str,
    #     lesson: Lesson,
    #     was_paid: bool = False
    # ) -> bool:
    #     """
    #     Уведомить репетитора об отмене занятия учеником.
        
    #     Args:
    #         bot: Экземпляр бота
    #         tutor_telegram_id: Telegram ID репетитора
    #         student_name: Имя ученика
    #         lesson: Объект занятия
    #         was_paid: Было ли занятие оплачено
        
    #     Returns:
    #         bool: True, если уведомление отправлено успешно
    #     """
    #     date_str = lesson.start_time.strftime("%d.%m.%Y")
    #     time_str = lesson.start_time.strftime("%H:%M")
        
    #     text = (
    #         f"📢 **Ученик отменил занятие!**\n\n"
    #         f"👤 {student_name or 'Ученик'}\n"
    #         f"📅 Дата: {date_str}\n"
    #         f"⏰ Время: {time_str}"
    #     )
        
    #     if was_paid:
    #         text += "\n\n💰 Занятие было оплачено."
    #     else:
    #         text += "\n\n💰 Занятие не было оплачено."
        
    #     try:
    #         await bot.send_message(tutor_telegram_id, text, parse_mode="Markdown")
    #         logging.info(f"✅ Уведомление об отмене отправлено репетитору {tutor_telegram_id}")
    #         return True
    #     except Exception as e:
    #         logging.error(f"❌ Не удалось уведомить репетитора об отмене {tutor_telegram_id}: {e}")
    #         return False

    # @staticmethod
    # async def notify_payment_reminder(
    #     bot: Bot,
    #     student_telegram_id: int,
    #     student_name: str,
    #     amount: float,
    #     tutor_name: str
    # ) -> bool:
    #     """
    #     Отправить напоминание об оплате.
        
    #     Args:
    #         bot: Экземпляр бота
    #         student_telegram_id: Telegram ID ученика
    #         student_name: Имя ученика
    #         amount: Сумма к оплате
    #         tutor_name: Имя репетитора
        
    #     Returns:
    #         bool: True, если уведомление отправлено успешно
    #     """
    #     text = (
    #         f"💰 **Напоминание об оплате!**\n\n"
    #         f"👤 Ученик: {student_name}\n"
    #         f"👨‍🏫 Репетитор: {tutor_name}\n"
    #         f"💳 Сумма к оплате: {amount} руб.\n\n"
    #         f"Пожалуйста, свяжитесь с репетитором для оплаты."
    #     )
        
    #     try:
    #         await bot.send_message(student_telegram_id, text, parse_mode="Markdown")
    #         logging.info(f"✅ Напоминание об оплате отправлено ученику {student_telegram_id}")
    #         return True
    #     except Exception as e:
    #         logging.error(f"❌ Не удалось отправить напоминание об оплате {student_telegram_id}: {e}")
    #         return False

    # @staticmethod
    # async def notify_tutor_about_missed_lesson(
    #     bot: Bot,
    #     tutor_telegram_id: int,
    #     student_name: str,
    #     lesson: Lesson
    # ) -> bool:
    #     """
    #     Уведомить репетитора о пропущенном занятии.
        
    #     Args:
    #         bot: Экземпляр бота
    #         tutor_telegram_id: Telegram ID репетитора
    #         student_name: Имя ученика
    #         lesson: Объект занятия
        
    #     Returns:
    #         bool: True, если уведомление отправлено успешно
    #     """
    #     date_str = lesson.start_time.strftime("%d.%m.%Y")
    #     time_str = lesson.start_time.strftime("%H:%M")
        
    #     text = (
    #         f"⚠️ **Занятие отмечено как пропущенное!**\n\n"
    #         f"👤 Ученик: {student_name or 'Ученик'}\n"
    #         f"📅 Дата: {date_str}\n"
    #         f"⏰ Время: {time_str}\n"
    #         f"⏱ Длительность: {lesson.duration_minutes} мин\n\n"
    #         f"Занятие не было проведено."
    #     )
        
    #     try:
    #         await bot.send_message(tutor_telegram_id, text, parse_mode="Markdown")
    #         logging.info(f"✅ Уведомление о пропущенном занятии отправлено репетитору {tutor_telegram_id}")
    #         return True
    #     except Exception as e:
    #         logging.error(f"❌ Не удалось уведомить репетитора {tutor_telegram_id}: {e}")
    #         return False

    # @staticmethod
    # async def send_bulk_notification(
    #     bot: Bot,
    #     user_ids: list[int],
    #     text: str,
    #     parse_mode: str = "Markdown"
    # ) -> dict:
    #     """
    #     Отправить массовое уведомление нескольким пользователям.
        
    #     Args:
    #         bot: Экземпляр бота
    #         user_ids: Список Telegram ID
    #         text: Текст уведомления
    #         parse_mode: Режим парсинга
        
    #     Returns:
    #         dict: {
    #             "success": int,
    #             "failed": int,
    #             "errors": list
    #         }
    #     """
    #     result = {
    #         "success": 0,
    #         "failed": 0,
    #         "errors": []
    #     }
        
    #     for user_id in user_ids:
    #         try:
    #             await bot.send_message(user_id, text, parse_mode=parse_mode)
    #             result["success"] += 1
    #         except Exception as e:
    #             result["failed"] += 1
    #             result["errors"].append({"user_id": user_id, "error": str(e)})
    #             logging.error(f"❌ Не удалось отправить уведомление {user_id}: {e}")
        
    #     logging.info(f"📊 Массовое уведомление: {result['success']} успешно, {result['failed']} ошибок")
    #     return result