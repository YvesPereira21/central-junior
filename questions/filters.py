import django_filters
from questions.models import Question


class QuestionFilter(django_filters.FilterSet):
    created_at = django_filters.NumberFilter(field_name='created_at', lookup_expr='year')

    first_name = django_filters.CharFilter(
        field_name='author__user__first_name',
        lookup_expr='icontains'
    )
    last_name = django_filters.CharFilter(
        field_name='author__user__last_name',
        lookup_expr='icontains'
    )

    is_solutioned = django_filters.BooleanFilter(field_name='is_solutioned')

    technologies = django_filters.CharFilter(field_name='technologies__name')

    class Meta:
        model = Question
        fields = ['created_at', 'first_name', 'last_name', 'is_solutioned', 'technologies']
