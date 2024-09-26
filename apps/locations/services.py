from django.db import transaction, models
from django.db.models import (
    Prefetch,
    IntegerField,
    Case,
    When,
    Count,
    ExpressionWrapper,
    F,
    DecimalField,
    Subquery,
    OuterRef,
    Sum,
)
from django.db.models.functions import Coalesce, Greatest, Extract
from django.utils import timezone

from apps.containers.models import ContainerStorage
from apps.core.choices import ContainerSize
from apps.locations.filters import ContainerLocationFilter
from apps.locations.models import Yard, ContainerLocation


class YardService:
    def get_all(self, filters=None):
        current_time = timezone.now()

        # Optimize container location query
        qs = ContainerLocation.objects.all()
        if filters:
            qs = ContainerLocationFilter(filters, queryset=qs).qs

        # Prefetch related container data with total_cost calculation
        terminal_visits_qs = ContainerStorage.objects.annotate_storage_costs()
        qs = (
            qs.select_related("container")
            .prefetch_related(
                Prefetch("terminal_visits", queryset=terminal_visits_qs),
                "terminal_visits__customer",
            )
            .only(
                "id",
                "row",
                "column_start",
                "column_end",
                "tier",
                "yard_id",
                "container__id",
                "container__name",
                "container__type",
                "terminal_visits__entry_time",
                "terminal_visits__customer__name",
                "terminal_visits__entry_time",
                "terminal_visits__is_empty",
                "terminal_visits__customer__name",
                "terminal_visits__customer__id",
            )
        )

        # Optimize yard query with prefetched container locations and total storage cost
        yard_qs = Yard.objects.annotate(
            total_yard_storage_cost=Subquery(
                ContainerStorage.objects.filter(container_location__yard=OuterRef("pk"))
                .annotate(
                    total_cost=ExpressionWrapper(
                        Greatest(Extract(current_time - F("entry_time"), "day") + 1, 1)
                        * Coalesce("storage_cost__daily_rate", 0),
                        output_field=DecimalField(max_digits=10, decimal_places=2),
                    )
                )
                .values("container_location__yard")
                .annotate(sum_total_cost=Sum("total_cost"))
                .values("sum_total_cost")[:1]
            )
        )

        if filters and filters.get("yard_id", None):
            yards = yard_qs.filter(id=filters.get("yard_id")).prefetch_related(
                Prefetch("container_locations", queryset=qs)
            )
        else:
            yards = (
                yard_qs.all()
                .prefetch_related(Prefetch("container_locations", queryset=qs))
                .order_by("name")
            )

        result = []
        for yard in yards:
            yard_data = {
                "id": yard.id,
                "name": yard.name,
                "max_rows": yard.max_rows,
                "max_columns": yard.max_columns,
                "max_tiers": yard.max_tiers,
                "x_coordinate": yard.x_coordinate,
                "z_coordinate": yard.z_coordinate,
                "rotation_degree": yard.rotation_degree,
                "total_yard_storage_cost": yard.total_yard_storage_cost or 0,
                "container_locations": [
                    {
                        "id": loc.id,
                        "row": loc.row,
                        "column_start": loc.column_start,
                        "column_end": loc.column_end,
                        "tier": loc.tier,
                        "container": {
                            "id": loc.container.id,
                            "name": loc.container.name,
                            "type": loc.container.type,
                            "customer": {
                                "id": loc.terminal_visits.first().company.id,
                                "name": loc.terminal_visits.first().company.name,
                            },
                            "entry_time": loc.terminal_visits.first().entry_time,
                            "storage_days": loc.terminal_visits.first().storage_days,
                            "is_empty": loc.terminal_visits.first().is_empty,
                            "total_storage_cost": loc.terminal_visits.first().total_storage_cost,
                        },
                    }
                    for loc in yard.container_locations.all()
                ],
            }
            result.append(yard_data)

        return result

    def get_places(self, container_type, customer_id):
        if customer_id:
            yards = Yard.objects.annotate(
                container_count=Coalesce(
                    Count(
                        "container_locations__container",
                        filter=models.Q(
                            container_locations__terminal_visits__customer_id=customer_id
                        ),
                    ),
                    0,
                    output_field=IntegerField(),
                ),
                has_containers=Case(
                    When(container_count__gt=0, then=1),
                    default=0,
                    output_field=IntegerField(),
                ),
            ).order_by("-has_containers", "-container_count")
        else:
            yards = Yard.objects.annotate(
                container_count=Count("container_locations")
            ).order_by("-container_count")

        result = []

        for yard in yards:
            available_places = self.get_available_places(yard, container_type)
            if available_places:
                data = {
                    "id": yard.id,
                    "name": yard.name,
                    "max_rows": yard.max_rows,
                    "max_columns": yard.max_columns,
                    "max_tiers": yard.max_tiers,
                    "available_places": available_places,
                    "container_count": yard.container_count,
                }
                result.append(data)
        return result

    def get_available_places(self, yard, container_type):
        columns_needed = 1 if container_type == ContainerSize.TWENTY else 2
        occupied_locations = ContainerLocation.objects.filter(yard=yard).values(
            "row", "column_start", "column_end", "tier", "container__type"
        )

        available_places = []

        for row in range(1, yard.max_rows + 1):
            for column in range(1, yard.max_columns - columns_needed + 2):
                for tier in range(1, yard.max_tiers + 1):
                    if self.is_place_available(
                        row, column, tier, columns_needed, occupied_locations
                    ) and self.is_supported(
                        row, column, tier, columns_needed, occupied_locations
                    ):
                        available_places.append(
                            {"row": row, "column_start": column, "tier": tier}
                        )

        return available_places

    def is_place_available(
        self, row, column_start, tier, columns_needed, occupied_locations
    ):
        column_end = column_start + columns_needed - 1
        for location in occupied_locations:
            if (
                location["row"] == row
                and location["tier"] == tier
                and not (
                    column_end < location["column_start"]
                    or column_start > location["column_end"]
                )
            ):
                return False
        return True

    def is_supported(self, row, column_start, tier, columns_needed, occupied_locations):
        if tier == 1:
            return True  # Ground level is always supported

        column_end = column_start + columns_needed - 1

        # Check for full support (single 40ft container or two 20ft containers)
        full_support = any(
            location["row"] == row
            and location["tier"] == tier - 1
            and location["column_start"] <= column_start
            and location["column_end"] >= column_end
            for location in occupied_locations
        )

        if full_support:
            return True

        # For 40ft containers, check if supported by two 20ft containers
        if columns_needed == 2:
            left_support = any(
                location["row"] == row
                and location["tier"] == tier - 1
                and location["column_start"] <= column_start
                and location["column_end"] >= column_start
                and location["container__type"] == ContainerSize.TWENTY
                for location in occupied_locations
            )

            right_support = any(
                location["row"] == row
                and location["tier"] == tier - 1
                and location["column_start"] <= column_end
                and location["column_end"] >= column_end
                and location["container__type"] == ContainerSize.TWENTY
                for location in occupied_locations
            )

            if left_support and right_support:
                return True

        return False

    @transaction.atomic
    def create(self, data):
        yard = Yard.objects.create(**data)
        return yard

    def update(self, yard_id, data):
        yard = Yard.objects.get(id=yard_id)
        for key, value in data.items():
            setattr(yard, key, value)
        yard.save()
        return yard


class ContainerLocationService:
    def create(self, container, data):
        if container.type == ContainerSize.TWENTY:
            data["column_end"] = data["column_start"]
        else:
            data["column_end"] = data["column_start"] + 1
        container_location = ContainerLocation.objects.create(
            container=container, **data
        )
        return container_location
