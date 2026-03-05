from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Habit(models.Model):
    # Константы для выбора периодичности
    PERIOD_DAILY = 1
    PERIOD_WEEKLY = 7
    PERIOD_CHOICES = [
        (PERIOD_DAILY, "Ежедневно"),
        (1, "Каждый день"),  # Для наглядности, можно добавить и другие дни
        (2, "Раз в 2 дня"),
        (3, "Раз в 3 дня"),
        (4, "Раз в 4 дня"),
        (5, "Раз в 5 дня"),
        (6, "Раз в 6 дня"),
        (PERIOD_WEEKLY, "Раз в неделю"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время выполнения")
    action = models.TextField(verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )
    linked_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_to",
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой (для полезных)",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        choices=PERIOD_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name="Периодичность (в днях)",
        help_text="Не реже 1 раза в 7 дней",
    )
    reward = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Вознаграждение"
    )
    duration_sec = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(120)],
        verbose_name="Время на выполнение (в секундах)",
        help_text="Не больше 120 секунд",
    )
    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")

    # Дополнительное поле для хранения chat_id пользователя в Telegram
    # Можно вынести в профиль пользователя, но для простоты оставим тут или в отдельной модели
    # Лучше создать отдельную модель UserProfile или расширить через OneToOne
    # chat_id = models.BigIntegerField(null=True, blank=True, verbose_name='Telegram chat ID')

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.action} в {self.time}"
