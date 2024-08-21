import django_filters
from django_filters import FilterSet

from apps.customers.models import Company


class CompanyFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    address = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Company
        fields = ["name", "address"]
