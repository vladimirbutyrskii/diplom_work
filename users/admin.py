from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Админ-панель для кастомной модели пользователя."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Личная информация'), {'fields': ('first_name', 'last_name', 'phone', 'image')}),
        (_('Роль'), {'fields': ('role',)}),
        (_('Права доступа'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Даты'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('created_at', 'updated_at')

