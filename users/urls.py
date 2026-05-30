from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    UserRegisterView,
    ResetPasswordRequestView,
    ResetPasswordConfirmView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    # JWT-токены
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Регистрация
    path("register/", UserRegisterView.as_view(), name="register"),
    # Сброс пароля
    path(
        "users/reset_password/",
        ResetPasswordRequestView.as_view(),
        name="reset_password",
    ),
    path(
        "users/reset_password_confirm/",
        ResetPasswordConfirmView.as_view(),
        name="reset_password_confirm",
    ),
]

urlpatterns += router.urls
