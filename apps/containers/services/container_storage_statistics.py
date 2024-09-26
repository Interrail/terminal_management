from django.db.models import F, Count
from django.utils import timezone

from apps.containers.models import ContainerStorage
from apps.core.choices import ContainerSize


class ContainerStorageStatisticsService:
    def get_container_storage_statistics(self):
        today = timezone.now().date()

        containers = ContainerStorage.objects.all()

        statistics = {
            "total_containers": containers.count(),
            "empty_containers": containers.filter(
                container_state__icontains="empty"
            ).count(),
            "loaded_containers": containers.filter(
                container_state__icontains="loaded"
            ).count(),
            "total_active_containers": containers.filter(
                exit_time__isnull=True
            ).count(),
            "total_dispatched_containers": containers.filter(
                exit_time__isnull=False
            ).count(),
            "new_arrived_containers": containers.filter(entry_time__gte=today).count(),
            "new_dispatched_containers": containers.filter(
                exit_time__isnull=False, entry_time__gte=today
            ).count(),
        }

        container_by_sizes = (
            ContainerStorage.objects.values(container_size=F("container__size"))
            .annotate(container_count=Count("id"))
            .order_by("container_size")
        )

        # Get all possible container sizes
        all_container_sizes = [size[0] for size in ContainerSize.choices]

        # Initialize a dictionary with all container sizes and a count of 0
        container_size_counts = {size: 0 for size in all_container_sizes}

        # Update the counts with the actual values from the query
        for size in container_by_sizes:
            container_size_counts[size["container_size"]] = size["container_count"]

        # Convert the dictionary to a list of dictionaries
        container_by_sizes = [
            {"container_size": size, "container_count": count}
            for size, count in container_size_counts.items()
        ]

        statistics["container_by_sizes"] = list(container_by_sizes)

        return statistics
