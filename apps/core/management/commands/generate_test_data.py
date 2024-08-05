import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.factories import (
    CompanyFactory,
    ContainerFactory,
    ContainerLocationFactory,
    ContainerTerminalVisitFactory,
    ContainerImageFactory,
    ContainerDocumentFactory,
)
from apps.locations.models import Yard


class Command(BaseCommand):
    help = (
        "Generates test data for Container related models including Yards and Locations"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--companies", type=int, default=25, help="Number of companies to create"
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
            # Create companies
            companies = [CompanyFactory() for _ in range(options["companies"])]
            self.stdout.write(self.style.SUCCESS(f"Created {len(companies)} companies"))

            yards = Yard.objects.all()
            container_locations = []
            terminal_visits = []

            for yard in yards:
                self.fill_yard(
                    yard,
                    options["fill_percentage"],
                    companies,
                    container_locations,
                    terminal_visits,
                )

            self.stdout.write(self.style.SUCCESS(f"Processed {len(yards)} yards"))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(container_locations)} container locations"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(terminal_visits)} container terminal visits"
                )
            )

            # Create container images (optional)
            if options["images"] > 0:
                images = [
                    ContainerImageFactory(container=random.choice(terminal_visits))
                    for _ in range(options["images"])
                ]
                self.stdout.write(
                    self.style.SUCCESS(f"Created {len(images)} container images")
                )

            # Create container documents (optional)
            if options["documents"] > 0:
                documents = [
                    ContainerDocumentFactory(container=random.choice(terminal_visits))
                    for _ in range(options["documents"])
                ]
                self.stdout.write(
                    self.style.SUCCESS(f"Created {len(documents)} container documents")
                )

            self.stdout.write(
                self.style.SUCCESS("Test data generation completed successfully")
            )

    def fill_yard(
        self, yard, fill_percentage, companies, container_locations, terminal_visits
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
            container_type = random.choice(["20", "40", "40HC"])

            if container_type == "20":
                columns_needed = 1
            else:
                columns_needed = 2

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
                    row=row
                    + 1,  # +1 because arrays are 0-indexed but yard is 1-indexed
                    column_start=col + 1,
                    column_end=col + columns_needed,
                    tier=tier,
                )
                container_locations.append(location)

                visit = ContainerTerminalVisitFactory(
                    container_location=location, customer=random.choice(companies)
                )
                terminal_visits.append(visit)

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
