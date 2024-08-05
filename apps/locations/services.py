from django.db import transaction
from django.db.models import Prefetch

from apps.containers.models import Container
from apps.locations.filters import ContainerLocationFilter
from apps.locations.models import Yard, ContainerLocation


class YardService:
    def get_all(self, filters=None):
        # Optimize container location query
        qs = ContainerLocation.objects.all()
        if filters:
            qs = ContainerLocationFilter(filters, queryset=qs).qs

        # Prefetch related container data
        qs = (
            qs.select_related("container")
            .prefetch_related("terminal_visits__customer")
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
                "terminal_visits__storage_days",
                "terminal_visits__is_empty",
                "terminal_visits__customer__name",
                "terminal_visits__customer__id",
            )
        )

        # Optimize yard query with prefetched container locations
        yards = Yard.objects.all().prefetch_related(
            Prefetch("container_locations", queryset=qs)
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
                                "id": loc.terminal_visits.first().customer.id,
                                "name": loc.terminal_visits.first().customer.name,
                            },
                            "entry_time": loc.terminal_visits.first().entry_time,
                            "storage_days": loc.terminal_visits.first().storage_days,
                            "is_empty": loc.terminal_visits.first().is_empty,
                        },
                    }
                    for loc in yard.container_locations.all()
                ],
            }
            result.append(yard_data)

        return result

    def get_places(self, container_type):
        yards = Yard.objects.all()
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
                }
                result.append(data)
        return result

    def get_available_places(self, yard, container_type):
        columns_needed = 1 if container_type == Container.ContainerType.TWENTY else 2
        occupied_locations = ContainerLocation.objects.filter(yard=yard).values(
            "row", "column_start", "column_end", "tier"
        )

        available_places = []

        for row in range(1, yard.max_rows + 1):
            for column in range(1, yard.max_columns - columns_needed + 2):
                for tier in range(1, yard.max_tiers + 1):
                    if self.is_place_available(
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
        if container.type == container.ContainerType.TWENTY:
            data["column_end"] = data["column_start"]
        else:
            data["column_end"] = data["column_start"] + 1
        container_location = ContainerLocation.objects.create(
            container=container, **data
        )
        return container_location
