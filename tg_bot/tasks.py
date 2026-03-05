import requests
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from habits.models import Habit
from tg_bot.models import TelegramUser
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, text):
    """Вспомогательная функция для отправки сообщения в Telegram."""
    token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        logger.info(f"Message sent to {chat_id}: {text[:50]}...")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
        return False


@shared_task
def send_habit_reminders():
    """Задача для поиска привычек, которые нужно выполнить, и отправки напоминаний."""
    now = timezone.now()

    # Получаем все привычки, время которых соответствует текущему часу
    # Например, если сейчас 15:30, найдем привычки с временем с 15:00 до 15:59
    start_time = (now - timedelta(
        minutes=now.minute,
        seconds=now.second,
        microsecond=now.microsecond
    )).time()

    end_time = (now + timedelta(hours=1) - timedelta(
        minutes=now.minute,
        seconds=now.second,
        microsecond=now.microsecond
    )).time()

    habits_to_notify = Habit.objects.filter(
        time__gte=start_time,
        time__lt=end_time
    ).select_related('user__telegram_profile')

    for habit in habits_to_notify:
        # Проверяем, есть ли у пользователя Telegram профиль с chat_id
        try:
            tg_user = habit.user.telegram_profile
            if not tg_user.verified:
                logger.info(f"User {habit.user.username} has unverified Telegram chat.")
                continue

            # Формируем сообщение
            if habit.linked_habit:
                reward_text = habit.linked_habit.action
            elif habit.reward:
                reward_text = habit.reward
            else:
                reward_text = "не указана"

            message = (
                f"🔔 Напоминание о привычке!\n\n"
                f"<b>{habit.action}</b>\n"
                f"📍 Место: {habit.place}\n"
                f"⏰ Время: {habit.time.strftime('%H:%M')}\n"
                f"⏱ Длительность: {habit.duration_sec} сек.\n"
                f"🏆 Награда: {reward_text}"
            )
            send_telegram_message.delay(tg_user.chat_id, message)

        except TelegramUser.DoesNotExist:
            logger.info(f"User {habit.user.username} has no Telegram profile.")
