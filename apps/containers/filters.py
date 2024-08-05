import django_filters
from django_filters import FilterSet


class ContainerStorageFilter(FilterSet):
    container = django_filters.CharFilter(
        field_name="container_location__container__name", lookup_expr="icontains"
    )
    types = django_filters.CharFilter(method="filter_type")
    customer = django_filters.CharFilter(
        field_name="customer__name", lookup_expr="icontains"
    )
    is_empty = django_filters.BooleanFilter()
    entry_time = django_filters.DateFilter(field_name="entry_time__date")
    storage_days = django_filters.NumberFilter(field_name="storage_days")
    notes = django_filters.CharFilter(field_name="notes", lookup_expr="icontains")

    def filter_type(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(container_location__container__type__in=values)
