import os
import django
from django.test import TestCase
from django.contrib.auth.models import User
from habits.models import Habit
from django.utils import timezone
from datetime import time, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

# Убеждаемся, что настройки Django загружены
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


class HabitModelTest(TestCase):
    """Тесты для модели Habit"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.habit_data = {
            "user": self.user,
            "place": "Дом",
            "time": time(8, 0),
            "action": "Сделать зарядку",
            "is_pleasant": False,
            "periodicity": 1,
            "duration_sec": 60,
            "is_public": False,
            "reward": "Шоколадка",
        }

    def test_create_habit(self):
        """Тест создания привычки"""
        habit = Habit.objects.create(**self.habit_data)

        self.assertEqual(habit.user, self.user)
        self.assertEqual(habit.place, "Дом")
        self.assertEqual(habit.time, time(8, 0))
        self.assertEqual(habit.action, "Сделать зарядку")
        self.assertFalse(habit.is_pleasant)
        self.assertEqual(habit.periodicity, 1)
        self.assertEqual(habit.duration_sec, 60)
        self.assertFalse(habit.is_public)
        self.assertEqual(habit.reward, "Шоколадка")
        self.assertIsNone(habit.linked_habit)

    def test_habit_str_method(self):
        """Тест строкового представления модели"""
        habit = Habit.objects.create(**self.habit_data)
        expected_str = "Сделать зарядку в 08:00:00"
        self.assertEqual(str(habit), expected_str)


class HabitAPITestCase(APITestCase):
    """Тесты для API эндпоинтов привычек"""

    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            username="user1", password="testpass123", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="testpass123", email="user2@example.com"
        )

        # Аутентифицируем первого пользователя
        self.client.force_authenticate(user=self.user1)

        # Базовые данные для привычки
        self.habit_data = {
            "place": "Дом",
            "time": "08:00:00",
            "action": "Сделать зарядку",
            "is_pleasant": False,
            "periodicity": 1,
            "duration_sec": 60,
            "is_public": False,
            "reward": "Шоколадка",
        }

        # URL для эндпоинтов
        self.habits_url = reverse("habit-list")
        self.public_habits_url = reverse("public-habits")

    def test_create_habit(self):
        """Тест создания привычки"""
        response = self.client.post(self.habits_url, self.habit_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)

        habit = Habit.objects.get()
        self.assertEqual(habit.user, self.user1)
        self.assertEqual(habit.place, self.habit_data["place"])
        self.assertEqual(habit.action, self.habit_data["action"])

    def test_create_habit_without_auth(self):
        """Тест создания привычки без аутентификации"""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.habits_url, self.habit_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_habits_list(self):
        """Тест получения списка публичных привычек"""
        # Создаем публичную привычку для user1
        Habit.objects.create(
            user=self.user1,
            place="Дом",
            time="08:00:00",
            action="Публичная привычка 1",
            duration_sec=60,
            periodicity=1,
            is_public=True,
            reward="Награда 1",
        )

        # Создаем приватную привычку для user1 (не должна быть в списке)
        Habit.objects.create(
            user=self.user1,
            place="Дом",
            time="09:00:00",
            action="Приватная привычка",
            duration_sec=60,
            periodicity=1,
            is_public=False,
        )

        # Создаем публичную привычку для user2
        Habit.objects.create(
            user=self.user2,
            place="Офис",
            time="10:00:00",
            action="Публичная привычка 2",
            duration_sec=60,
            periodicity=1,
            is_public=True,
            reward="Награда 2",
        )

        # Получаем список публичных привычек
        response = self.client.get(self.public_habits_url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что в ответе только публичные привычки (должно быть 2)
        self.assertEqual(len(response.data["results"]), 2)

        # Проверяем, что приватная привычка не попала в список
        actions = [habit["action"] for habit in response.data["results"]]
        self.assertIn("Публичная привычка 1", actions)
        self.assertIn("Публичная привычка 2", actions)
        self.assertNotIn("Приватная привычка", actions)

        # Проверяем, что все привычки действительно публичные
        for habit_data in response.data["results"]:
            self.assertTrue(habit_data["is_public"])

    def test_list_habits(self):
        """Тест получения списка привычек пользователя"""
        # Создаем 3 привычки для user1
        for i in range(3):
            Habit.objects.create(
                user=self.user1,
                place=f"Место {i}",
                time="08:00:00",
                action=f"Привычка {i}",
                duration_sec=60,
                periodicity=1,
            )

        # Создаем привычку для user2
        Habit.objects.create(
            user=self.user2,
            place="Офис",
            time="09:00:00",
            action="Чужая привычка",
            duration_sec=60,
            periodicity=1,
        )

        response = self.client.get(self.habits_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны быть только привычки user1 (3 шт.)
        self.assertEqual(len(response.data["results"]), 3)
