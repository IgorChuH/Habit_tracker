import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("habits_tracker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Настройка периодической задачи (Celery Beat)
app.conf.beat_schedule = {
    "send-habit-reminders": {
        "task": "tg_bot.tasks.send_habit_reminders",
        # Запускать каждый час (например, в 0 минут каждого часа)
        "schedule": crontab(minute=0),
    },
}
