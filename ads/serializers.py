from rest_framework import serializers

from .models import Ad, Comment


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва."""

    author_email = serializers.EmailField(source="author.email", read_only=True)
    author_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "author",
            "author_email",
            "author_name",
            "ad",
            "created_at",
        )
        read_only_fields = ("id", "author", "ad", "created_at")

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"


class AdListSerializer(serializers.ModelSerializer):
    """Сериализатор объявления для списка (без полного описания)."""

    author_email = serializers.EmailField(source="author.email", read_only=True)
    author_name = serializers.SerializerMethodField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ad
        fields = (
            "id",
            "title",
            "price",
            "author_email",
            "author_name",
            "comments_count",
            "created_at",
        )
        read_only_fields = ("id", "author", "created_at")

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"

    def get_comments_count(self, obj):
        return obj.comments.count()


class AdDetailSerializer(serializers.ModelSerializer):
    """Сериализатор объявления для детального просмотра (с описанием и отзывами)."""

    author_email = serializers.EmailField(source="author.email", read_only=True)
    author_name = serializers.SerializerMethodField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ad
        fields = (
            "id",
            "title",
            "price",
            "description",
            "author",
            "author_email",
            "author_name",
            "comments",
            "created_at",
        )
        read_only_fields = ("id", "author", "created_at")

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования объявления."""

    class Meta:
        model = Ad
        fields = (
            "title",
            "price",
            "description",
        )
