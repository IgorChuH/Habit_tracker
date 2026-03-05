from rest_framework import permissions


class IsOwnerOrReadOnlyPublic(permissions.BasePermission):
    """
    Разрешение на уровне объекта: только владелец может редактировать/удалять.
    При этом, если привычка публичная, любой пользователь может её видеть (но не менять).
    """

    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS запросы разрешены всегда (для чтения)
        if request.method in permissions.SAFE_METHODS:
            # Разрешаем просмотр, если привычка публичная ИЛИ это владелец
            return obj.is_public or obj.user == request.user
        # Запросы на изменение (PUT, PATCH, DELETE) разрешены только владельцу
        return obj.user == request.user
