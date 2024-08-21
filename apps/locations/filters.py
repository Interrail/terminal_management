import django_filters


class ContainerLocationFilter(django_filters.FilterSet):
    container_name = django_filters.CharFilter(
        field_name="container__name", lookup_expr="icontains"
    )
    container_types = django_filters.CharFilter(method="filter_type")
    customer_name = django_filters.CharFilter(method="filter_customer_name")
    is_empty = django_filters.BooleanFilter(field_name="terminal_visits__is_empty")
    date = django_filters.DateFilter(field_name="terminal_visits__entry_time__date")
    storage_days = django_filters.NumberFilter(
        field_name="terminal_visits__storage_days"
    )
    notes = django_filters.CharFilter(
        field_name="terminal_visits__notes", lookup_expr="icontains"
    )

    def filter_type(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(container__type__in=values)

    def filter_customer_name(self, queryset, name, value):
        return queryset.filter(terminal_visits__customer__name__icontains=value)
