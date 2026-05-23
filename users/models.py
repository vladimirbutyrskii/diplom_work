# Create your models here.
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер пользователей, где email используется как логин."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ADMIN = 'admin', 'Администратор'

    # Убираем username, делаем email основным логином
    username = None
    email = models.EmailField('Электронная почта', unique=True)

    # Дополнительные поля
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    image = models.ImageField('Аватарка', upload_to='avatars/', blank=True, null=True)

    # Переопределяем поля из AbstractUser
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)

    # Поля для отслеживания
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
