from django.shortcuts import get_object_or_404

from .filters import UserFilter
from .models import CustomUser


class UserService:
    def get_all(self, filters=None):
        filters = filters or {}
        qs = CustomUser.objects.all()
        return UserFilter(filters, queryset=qs).qs

    def get_by_id(self, user_id):
        return get_object_or_404(CustomUser, id=user_id)
