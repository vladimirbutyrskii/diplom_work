from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsOwnerOrAdmin

from .models import User
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordConfirmSerializer,
)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    Просмотр, редактирование и удаление профиля пользователя.
    Пользователь может работать только со своим профилем.
    Администратор — с любым профилем.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'pk'

    # def get_object(self):
    #     return self.request.user

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        """Эндпоинт для получения и редактирования своего профиля."""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class UserRegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class ResetPasswordRequestView(generics.GenericAPIView):
    """Отправка письма со ссылкой для сброса пароля."""
    serializer_class = ResetPasswordRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Не раскрываем, существует ли email в базе
            return Response(
                {'detail': 'Ссылка для сброса пароля отправлена на почту.'},
                status=status.HTTP_200_OK,
            )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # В реальном проекте здесь будет отправка email
        # Для разработки выводим ссылку в консоль
        reset_link = f'http://localhost:8000/api/users/reset_password_confirm/?uid={uid}&token={token}'
        print(f'\n=== ССЫЛКА ДЛЯ СБРОСА ПАРОЛЯ ===\n{reset_link}\n==============================\n')

        return Response(
            {'detail': 'Ссылка для сброса пароля отправлена на почту.'},
            status=status.HTTP_200_OK,
        )


class ResetPasswordConfirmView(generics.GenericAPIView):
    """Подтверждение сброса пароля и установка нового."""
    serializer_class = ResetPasswordConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {'error': 'Недействительная ссылка для сброса пароля.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Токен сброса пароля недействителен или истёк.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {'detail': 'Пароль успешно изменён.'},
            status=status.HTTP_200_OK,
        )

