import django_filters
from django.db.models import Q
from django_filters import FilterSet

from apps.customers.models import Company


class CompanyFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    address = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Company
        fields = ["name", "address"]


class CompanyServiceFilter(FilterSet):
    container_size = django_filters.CharFilter(method="filter_container_size")
    container_state = django_filters.CharFilter(method="filter_state")

    def filter_container_size(self, queryset, name, value):
        return queryset.filter(
            Q(service__container_size=value) | Q(service__container_size="any")
        )

    def filter_state(self, queryset, name, value):
        return queryset.filter(
            Q(service__container_state=value) | Q(service__container_state="any")
        )


class FreeDaysFilter(FilterSet):
    container_size = django_filters.CharFilter(
        field_name="free_day_combination__container_size"
    )
    container_state = django_filters.CharFilter(
        field_name="free_day_combination__container_state"
    )
    category = django_filters.CharFilter(field_name="free_day_combination__category")
