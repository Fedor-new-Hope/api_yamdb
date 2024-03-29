from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter

from reviews.models import Title


class FilterTitle(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='contains')
    genre = CharFilter(field_name='genre__slug', lookup_expr='contains')
    category = CharFilter(field_name='category__slug', lookup_expr='contains')
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = '__all__'
