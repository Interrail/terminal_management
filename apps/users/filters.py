import django_filters
from django_filters import FilterSet

from apps.users.models import CustomUser


class UserFilter(FilterSet):
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    username = django_filters.CharFilter(lookup_expr="icontains")
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()
    is_superuser = django_filters.BooleanFilter()

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
