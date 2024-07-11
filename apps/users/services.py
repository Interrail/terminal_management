from .filters import UserFilter
from .models import CustomUser


class UserService:
    def get_all(self, filters=None):
        filters = filters or {}
        qs = CustomUser.objects.all()
        return UserFilter(filters, queryset=qs).qs
