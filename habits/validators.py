from rest_framework.serializers import ValidationError


class RewardAndLinkedHabitValidator:
    """Исключить одновременный выбор связанной привычки и указания вознаграждения."""

    def __call__(self, data):
        linked_habit = data.get("linked_habit")
        reward = data.get("reward")
        if linked_habit and reward:
            raise ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку. "
                "Заполните только одно из полей."
            )


class DurationValidator:
    """Время выполнения должно быть не больше 120 секунд."""

    def __call__(self, data):
        duration = data.get("duration_sec")
        if duration and duration > 120:
            raise ValidationError(
                f"Время выполнения ({duration} сек.) не должно превышать 120 секунд."
            )


class LinkedHabitIsPleasantValidator:
    """В связанные привычки могут попадать только привычки с признаком приятной привычки."""

    def __call__(self, data):
        linked_habit = data.get("linked_habit")
        if linked_habit and not linked_habit.is_pleasant:
            raise ValidationError(
                "Связанная привычка должна иметь признак приятной привычки."
            )


class PleasantHabitNoRewardOrLinkedValidator:
    """У приятной привычки не может быть вознаграждения или связанной привычки."""

    def __call__(self, data):
        is_pleasant = data.get("is_pleasant")
        linked_habit = data.get("linked_habit")
        reward = data.get("reward")

        if is_pleasant and (linked_habit or reward):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )


class PeriodicityValidator:
    """Нельзя выполнять привычку реже, чем 1 раз в 7 дней."""

    def __call__(self, data):
        period = data.get("periodicity")
        if period and period > 7:
            raise ValidationError(
                f"Периодичность выполнения не может быть реже 1 раза в 7 дней. "
                f"Указано: раз в {period} дней."
            )
