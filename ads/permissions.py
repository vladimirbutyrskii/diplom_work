from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Доступ разрешён:
    - Администратору (role='admin' или is_superuser) — для любых действий.
    - Владельцу объекта — для редактирования и удаления.
    - Остальным — только безопасные методы (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
        # Админ или суперпользователь — полный доступ
        if request.user.is_authenticated and request.user.is_admin:
            return True

        # Владелец — полный доступ
        if hasattr(obj, "author") and obj.author == request.user:
            return True

        # Остальные аутентифицированные — только чтение
        if request.method in permissions.SAFE_METHODS:
            return True

        return False


class IsAuthenticatedOrReadOnlyForCreate(permissions.BasePermission):
    """
    Создавать могут только аутентифицированные пользователи.
    Читать — все (включая анонимов).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
