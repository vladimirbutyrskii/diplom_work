from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Доступ к профилю:
    - Администратор — полный доступ.
    - Владелец профиля — просмотр и редактирование своего профиля.
    - Остальные — без доступа.
    """

    def has_object_permission(self, request, view, obj):
        # Админ или суперпользователь — полный доступ
        if request.user.is_authenticated and request.user.is_admin:
            return True

        # Пользователь может работать только со своим профилем
        return obj == request.user
