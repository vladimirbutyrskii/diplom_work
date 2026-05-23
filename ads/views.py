from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

from .filters import AdFilter
from .models import Ad, Comment
from .permissions import IsOwnerOrAdmin, IsAuthenticatedOrReadOnlyForCreate
from .serializers import (
    AdListSerializer,
    AdDetailSerializer,
    AdCreateUpdateSerializer,
    CommentSerializer,
)


class AdPagination(PageNumberPagination):
    """Пагинация для объявлений — максимум 4 на странице."""
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 4


class AdViewSet(viewsets.ModelViewSet):
    """ViewSet для объявлений."""

    queryset = Ad.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnlyForCreate, IsOwnerOrAdmin]
    pagination_class = AdPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AdFilter
    search_fields = ['title']

    def get_serializer_class(self):
        if self.action == 'list':
            return AdListSerializer
        elif self.action == 'retrieve':
            return AdDetailSerializer
        else:  # create, update, partial_update
            return AdCreateUpdateSerializer

    def perform_create(self, serializer):
        """При создании объявления автоматически подставляем автора."""
        serializer.save(author=self.request.user)

    def get_permissions(self):
        # Для создания требуется аутентификация
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """Возвращаем отзывы только для конкретного объявления."""
        ad_id = self.kwargs.get('ad_pk')
        return Comment.objects.filter(ad_id=ad_id)

    def perform_create(self, serializer):
        """При создании отзыва подставляем автора и объявление."""
        ad_id = self.kwargs.get('ad_pk')
        serializer.save(
            author=self.request.user,
            ad_id=ad_id,
        )

