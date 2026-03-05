from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Habit
from .serializers import HabitSerializer, HabitPublicSerializer
from .permissions import IsOwnerOrReadOnlyPublic


class HabitPagination(PageNumberPagination):
    """Пагинация по 5 элементов на странице."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с привычками текущего пользователя."""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyPublic]
    pagination_class = HabitPagination

    def get_queryset(self):
        # Возвращаем только привычки текущего пользователя
        # (для списка и других операций)
        return Habit.objects.filter(user=self.request.user)


class PublicHabitListView(generics.ListAPIView):
    """Эндпоинт для просмотра списка публичных привычек."""

    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitPublicSerializer
    permission_classes = [IsAuthenticated]  # Только для авторизованных пользователей
    pagination_class = HabitPagination
