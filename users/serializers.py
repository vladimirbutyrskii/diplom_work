from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения и обновления пользователя."""

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'image',
        )
        read_only_fields = ('id', 'role')


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'phone',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса на сброс пароля."""
    email = serializers.EmailField()


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения сброса пароля."""
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
