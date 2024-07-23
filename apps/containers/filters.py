import django_filters
from django_filters import FilterSet


class ContainerTerminalVisitFilter(FilterSet):
    container = django_filters.CharFilter(
        field_name="container__name", lookup_expr="icontains"
    )
    types = django_filters.CharFilter(method="filter_type")
    customer = django_filters.CharFilter(
        field_name="customer__name", lookup_expr="icontains"
    )
    is_empty = django_filters.BooleanFilter()

    def filter_type(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(container__type__in=values)
