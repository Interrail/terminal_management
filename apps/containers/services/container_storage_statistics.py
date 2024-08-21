from django.db.models import F, Count, Q

from apps.containers.models import ContainerStorage


class ContainerStorageStatisticsService:
    def get_container_types(self, customer_id=None, status=None):
        base_query = ContainerStorage.objects.all()

        if customer_id:
            base_query = base_query.filter(customer_id=customer_id)

        if status == "in_terminal":
            base_query = base_query.filter(exit_time__isnull=True)
        elif status == "left_terminal":
            base_query = base_query.filter(exit_time__isnull=False)

        return list(
            base_query.annotate(type=F("container__type"))
            .values("type")
            .annotate(
                count=Count("container__type"),
                empty_count=Count("container__type", filter=Q(is_empty=True)),
                laden_count=Count("container__type", filter=Q(is_empty=False)),
            )
            .order_by("-count")
        )
