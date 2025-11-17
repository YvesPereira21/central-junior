import django_filters
from articles.models import Article


class ArticleFilter(django_filters.FilterSet):
    created_at = django_filters.NumberFilter(field_name='created_at', lookup_expr='year')

    first_name = django_filters.CharFilter(
        field_name='profile__user__first_name',
        lookup_expr='icontains'
    )
    last_name = django_filters.CharFilter(
        field_name='profile__user__last_name',
        lookup_expr='icontains'
    )

    technologies = django_filters.CharFilter(field_name='technologies__name')

    class Meta:
        model = Article
        fields = ['created_at', 'first_name', 'last_name', 'technologies']
