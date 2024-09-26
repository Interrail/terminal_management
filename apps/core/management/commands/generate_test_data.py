import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.choices import ContainerSize
from apps.core.factories import (
    CompanyFactory,
    ContainerFactory,
    ContainerLocationFactory,
    ContainerStorageFactory,
    ContainerImageFactory,
    ContainerDocumentFactory,
    CustomerStorageCostFactory,
)
from apps.finance.models import CustomerStorageCost
from apps.locations.models import Yard


class Command(BaseCommand):
    help = "Generates test data for Container related models including Locations and Storages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--companies", type=int, default=10, help="Number of companies to create"
        )
        parser.add_argument(
            "--fill_percentage",
            type=int,
            default=50,
            help="Percentage of yard to fill (0-100)",
        )
        parser.add_argument(
            "--images",
            type=int,
            default=10,
            help="Number of container images to create",
        )
        parser.add_argument(
            "--documents",
            type=int,
            default=10,
            help="Number of container documents to create",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            # Create companies and their price lists
            companies = [CompanyFactory() for _ in range(options["companies"])]
            self.create_price_lists(companies)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(companies)} companies with price lists"
                )
            )

            yards = Yard.objects.all()
            container_locations = []
            container_storages = []

            for yard in yards:
                self.fill_yard(
                    yard,
                    options["fill_percentage"],
                    companies,
                    container_locations,
                    container_storages,
                )

            self.stdout.write(self.style.SUCCESS(f"Processed {len(yards)} yards"))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(container_locations)} container locations"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(container_storages)} container storages"
                )
            )

            # Create container images and documents (optional)
            if options["images"] > 0:
                images = [
                    ContainerImageFactory(container=random.choice(container_storages))
                    for _ in range(options["images"])
                ]
                self.stdout.write(
                    self.style.SUCCESS(f"Created {len(images)} container images")
                )

            if options["documents"] > 0:
                documents = [
                    ContainerDocumentFactory(
                        container=random.choice(container_storages)
                    )
                    for _ in range(options["documents"])
                ]
                self.stdout.write(
                    self.style.SUCCESS(f"Created {len(documents)} container documents")
                )

            self.stdout.write(
                self.style.SUCCESS("Test data generation completed successfully")
            )

    def create_price_lists(self, companies):
        for company in companies:
            for container_type in ContainerSize.values:
                for is_empty in [True, False]:
                    CustomerStorageCostFactory(
                        customer=company,
                        container_type=container_type,
                        is_empty=is_empty,
                    )

    def fill_yard(
        self, yard, fill_percentage, companies, container_locations, container_storages
    ):
        yard_layout = [
            [0 for _ in range(yard.max_columns)] for _ in range(yard.max_rows)
        ]
        containers_to_create = (
            yard.max_rows * yard.max_columns * yard.max_tiers * fill_percentage
        ) // 100

        while containers_to_create > 0:
            row = random.randint(0, yard.max_rows - 1)
            col = random.randint(0, yard.max_columns - 1)
            container_type = random.choice(ContainerSize.values)

            columns_needed = 2 if container_type in ["40", "40HC", "45"] else 1

            if col + columns_needed > yard.max_columns:
                continue

            if self.can_place_container(
                yard_layout, row, col, columns_needed, yard.max_tiers
            ):
                tier = self.get_next_tier(yard_layout, row, col, columns_needed)

                container = ContainerFactory(type=container_type)
                location = ContainerLocationFactory(
                    container=container,
                    yard=yard,
                    row=row + 1,
                    column_start=col + 1,
                    column_end=col + columns_needed,
                    tier=tier,
                )
                container_locations.append(location)

                customer = random.choice(companies)
                is_empty = random.choice([True, False])

                # Get the existing CustomerStorageCost for this customer, container type, and empty status
                storage_cost = CustomerStorageCost.objects.get(
                    customer=customer, container_type=container_type, is_empty=is_empty
                )

                storage = ContainerStorageFactory(
                    container=container,
                    container_location=location,
                    customer=customer,
                    is_empty=is_empty,
                    storage_cost=storage_cost,
                )
                container_storages.append(storage)

                for i in range(columns_needed):
                    yard_layout[row][col + i] = tier

                containers_to_create -= 1

    def can_place_container(self, yard_layout, row, col, columns_needed, max_tiers):
        if any(yard_layout[row][col + i] >= max_tiers for i in range(columns_needed)):
            return False

        if columns_needed == 2:
            return yard_layout[row][col] == yard_layout[row][col + 1]

        return True

    def get_next_tier(self, yard_layout, row, col, columns_needed):
        return max(yard_layout[row][col + i] for i in range(columns_needed)) + 1
