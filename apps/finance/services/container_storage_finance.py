from apps.containers.models import ContainerStorage


class ContainerFinanceService:
    def get_container_list_finance(self, filters=None):
        filters = filters or {}
        qs = ContainerStorage.objects.select_related(
            "container", "company"
        ).prefetch_related("images", "documents", "services")
        return qs
