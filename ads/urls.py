from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers  # type: ignore

from .views import AdViewSet, CommentViewSet

# Основной роутер для объявлений
router = DefaultRouter()
router.register(r'ads', AdViewSet, basename='ads')

# Вложенный роутер для отзывов: /ads/{ad_pk}/comments/
ads_router = routers.NestedSimpleRouter(router, r'ads', lookup='ad')
ads_router.register(r'comments', CommentViewSet, basename='ad-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(ads_router.urls)),
]
