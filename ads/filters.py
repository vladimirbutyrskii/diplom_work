import django_filters

from .models import Ad


class AdFilter(django_filters.FilterSet):
    """Фильтр объявлений по названию."""

    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = Ad
        fields = ["title"]
