import pytest
from rest_framework.test import APIClient

from users.models import User


@pytest.fixture
def api_client():
    """Неавторизованный API-клиент."""
    return APIClient()


@pytest.fixture
def user_data():
    """Данные для создания пользователя."""
    return {
        "email": "user@example.com",
        "first_name": "Иван",
        "last_name": "Петров",
        "phone": "+79991234567",
        "password": "securepass123",
    }


@pytest.fixture
def user(db, user_data):
    """Обычный пользователь (роль user)."""
    user = User.objects.create_user(**user_data)
    return user


@pytest.fixture
def user_client(api_client, user):
    """API-клиент, авторизованный как обычный пользователь."""
    from rest_framework_simplejwt.tokens import AccessToken

    token = AccessToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    api_client.user = user
    return api_client


@pytest.fixture
def admin_data():
    """Данные для создания администратора."""
    return {
        "email": "admin@example.com",
        "first_name": "Админ",
        "last_name": "Админов",
        "password": "adminpass123",
    }


@pytest.fixture
def admin(db, admin_data):
    """Администратор (роль admin)."""
    admin = User.objects.create_user(**admin_data, role="admin")
    return admin


@pytest.fixture
def admin_client(api_client, admin):
    """API-клиент, авторизованный как администратор."""
    from rest_framework_simplejwt.tokens import AccessToken

    token = AccessToken.for_user(admin)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    api_client.user = admin
    return api_client


@pytest.fixture
def ad_data():
    """Данные для создания объявления."""
    return {
        "title": "Продам гараж",
        "price": 50000,
        "description": "Кирпичный, сухой, с ямой",
    }


@pytest.fixture
def ad(db, user, ad_data):
    """Объявление, созданное обычным пользователем."""
    from ads.models import Ad

    return Ad.objects.create(author=user, **ad_data)


@pytest.fixture
def comment_data():
    """Данные для создания отзыва."""
    return {
        "text": "Отличный гараж, рекомендую!",
    }


@pytest.fixture
def comment(db, user, ad, comment_data):
    """Отзыв, созданный обычным пользователем."""
    from ads.models import Comment

    return Comment.objects.create(author=user, ad=ad, **comment_data)
