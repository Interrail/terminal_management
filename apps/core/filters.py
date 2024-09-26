import django_filters
from django.db.models import Q
from django_filters import FilterSet


class TerminalServiceFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    base_price = django_filters.NumberFilter(lookup_expr="exact")
    service_type = django_filters.NumberFilter(field_name="service_type__id")
    container_size = django_filters.CharFilter(method="filter_container_size")
    container_state = django_filters.CharFilter(method="filter_state")
    unit_of_measure = django_filters.CharFilter(
        field_name="service_type__unit_of_measure", lookup_expr="exact"
    )

    def filter_container_size(self, queryset, name, value):
        return queryset.filter(Q(container_size=value) | Q(container_size="any"))

    def filter_state(self, queryset, name, value):
        return queryset.filter(Q(container_state=value) | Q(container_state="any"))


class TerminalServiceTypeFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    unit_of_measure = django_filters.CharFilter(lookup_expr="icontains")
