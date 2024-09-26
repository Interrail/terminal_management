import re

import django_filters
from django_filters import FilterSet


class ContainerStorageFilter(FilterSet):
    container_name = django_filters.CharFilter(
        field_name="container__name", lookup_expr="icontains"
    )
    container_size = django_filters.CharFilter(method="filter_container_sizes")
    types = django_filters.CharFilter(method="filter_type")
    company_name = django_filters.CharFilter(
        field_name="company__name", lookup_expr="icontains"
    )
    product_name = django_filters.CharFilter(lookup_expr="icontains")
    container_owner = django_filters.CharFilter(lookup_expr="icontains")
    transport_type = django_filters.CharFilter(lookup_expr="icontains")
    transport_number = django_filters.CharFilter(lookup_expr="icontains")
    exit_transport_type = django_filters.CharFilter(lookup_expr="icontains")
    exit_transport_number = django_filters.CharFilter(lookup_expr="icontains")
    entry_time = django_filters.CharFilter(field_name="filter_date")
    notes = django_filters.CharFilter(field_name="notes", lookup_expr="icontains")
    container_state = django_filters.CharFilter(lookup_expr="icontains")
    exit_time = django_filters.CharFilter(method="filter_date")
    active_services = django_filters.CharFilter(method="filter_active_services")
    dispatch_services = django_filters.CharFilter(method="filter_dispatch_services")

    def filter_container_sizes(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(container__size__in=values)

    def filter_active_services(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(active_services__service__service_type__id__in=values)

    def filter_dispatch_services(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(dispatch_services__service__service_type__id__in=values)

    def filter_date(self, queryset, name, value):
        value = str(value)

        # YYYY-MM-DD format
        if re.match(r"\d{4}-\d{2}-\d{2}$", value):
            return queryset.filter(**{f"{name}": value})

        # YYYY-MM format
        elif re.match(r"\d{4}-\d{2}$", value):
            year, month = value.split("-")
            return queryset.filter(**{f"{name}__year": year, f"{name}__month": month})

        # YYYY format
        elif re.match(r"\d{4}$", value):
            return queryset.filter(**{f"{name}__year": value})

        return queryset

    def filter_type(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(container__type__in=values)
