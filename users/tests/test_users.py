import pytest
from django.urls import reverse
from rest_framework import status

from users.models import User


# ============================================
# ТЕСТЫ РЕГИСТРАЦИИ
# ============================================


class TestUserRegistration:
    """Тесты регистрации пользователя."""

    @pytest.mark.django_db
    def test_register_success(self, api_client, user_data):
        """Успешная регистрация нового пользователя."""
        url = reverse("register")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == user_data["email"]
        assert response.data["first_name"] == user_data["first_name"]
        assert response.data["last_name"] == user_data["last_name"]
        assert "password" not in response.data
        assert User.objects.filter(email=user_data["email"]).exists()

    def test_register_duplicate_email(self, api_client, user, user_data):
        """Регистрация с уже существующим email."""
        url = reverse("register")
        response = api_client.post(url, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_register_missing_fields(self, api_client):
        """Регистрация без обязательных полей."""
        url = reverse("register")
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert "password" in response.data


# ============================================
# ТЕСТЫ JWT-ТОКЕНОВ
# ============================================


class TestJWTToken:
    """Тесты получения JWT-токенов."""

    def test_obtain_token_success(self, api_client, user, user_data):
        """Успешное получение токена с верными учётными данными."""
        url = reverse("token_obtain_pair")
        response = api_client.post(
            url,
            {
                "email": user_data["email"],
                "password": user_data["password"],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_obtain_token_wrong_password(self, api_client, user, user_data):
        """Ошибка при неверном пароле."""
        url = reverse("token_obtain_pair")
        response = api_client.post(
            url,
            {
                "email": user_data["email"],
                "password": "wrongpassword",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_obtain_token_nonexistent_user(self, api_client):
        """Ошибка при попытке входа несуществующего пользователя."""
        url = reverse("token_obtain_pair")
        response = api_client.post(
            url,
            {
                "email": "nonexistent@example.com",
                "password": "somepass",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_success(self, api_client, user):
        """Успешное обновление токена."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)

        url = reverse("token_refresh")
        response = api_client.post(url, {"refresh": str(refresh)}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


# ============================================
# ТЕСТЫ ПРОФИЛЯ
# ============================================


class TestUserProfile:
    """Тесты работы с профилем пользователя."""

    def test_get_own_profile(self, user_client, user):
        """Получение своего профиля."""
        url = reverse("users-me")
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert response.data["first_name"] == user.first_name

    def test_update_own_profile(self, user_client):
        """Обновление своего профиля."""
        url = reverse("users-me")
        response = user_client.patch(url, {"phone": "+79998887766"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["phone"] == "+79998887766"

    @pytest.mark.django_db
    def test_get_profile_unauthorized(self, api_client):
        """Попытка получения профиля без авторизации."""
        url = reverse("users-me")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_other_user_profile_by_admin(self, admin_client, user):
        """Администратор может просматривать профили других пользователей."""
        url = reverse("users-detail", args=[user.id])
        print(f"\nDEBUG: user.id={user.id}, user.email={user.email}")
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "user@example.com"

    def test_get_other_user_profile_by_user(self, user_client, admin):
        """Обычный пользователь не может просматривать чужие профили."""
        url = reverse("users-detail", args=[admin.id])
        response = user_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================
# ТЕСТЫ СБРОСА ПАРОЛЯ
# ============================================


class TestPasswordReset:
    """Тесты сброса пароля."""

    def test_reset_password_request_success(self, api_client, user):
        """Успешный запрос на сброс пароля."""
        url = reverse("reset_password")
        response = api_client.post(url, {"email": user.email}, format="json")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_reset_password_request_nonexistent(self, api_client):
        """Запрос на сброс пароля для несуществующего email."""
        url = reverse("reset_password")
        response = api_client.post(
            url, {"email": "nonexistent@example.com"}, format="json"
        )

        # Должен вернуть 200 даже для несуществующего email (безопасность)
        assert response.status_code == status.HTTP_200_OK

    def test_reset_password_confirm_invalid_token(self, api_client):
        """Подтверждение сброса с невалидным токеном."""
        url = reverse("reset_password_confirm")
        response = api_client.post(
            url,
            {
                "uid": "invalid",
                "token": "invalid",
                "new_password": "newpass123",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
