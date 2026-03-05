from rest_framework import serializers
from .models import Habit
from .validators import (
    RewardAndLinkedHabitValidator,
    DurationValidator,
    LinkedHabitIsPleasantValidator,
    PleasantHabitNoRewardOrLinkedValidator,
    PeriodicityValidator,
)


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Habit, включающий все валидаторы."""

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ["user"]  # Пользователь будет проставляться автоматически

    def validate(self, data):
        # Применяем все валидаторы
        RewardAndLinkedHabitValidator()(data)
        DurationValidator()(data)
        LinkedHabitIsPleasantValidator()(data)
        PleasantHabitNoRewardOrLinkedValidator()(data)
        PeriodicityValidator()(data)
        return data

    def create(self, validated_data):
        # Автоматически подставляем текущего пользователя при создании
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class HabitPublicSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек (только чтение)."""

    class Meta:
        model = Habit
        # Можно исключить чувствительные поля, если нужно, но пока оставим все
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "linked_habit",
            "periodicity",
            "reward",
            "duration_sec",
            "is_public",
        ]
