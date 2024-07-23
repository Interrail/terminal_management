from django.core.management.base import BaseCommand

from apps.containers.factories import (
    ContainerFactory,
    ContainerTerminalVisitFactory,
    ContainerImageFactory,
    ContainerDocumentFactory,
)
from apps.customers.factories import CompanyFactory


class Command(BaseCommand):
    help = "Generates test data for Container related models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--companies", type=int, default=5, help="Number of companies to create"
        )
        parser.add_argument(
            "--containers", type=int, default=20, help="Number of containers to create"
        )
        parser.add_argument(
            "--visits",
            type=int,
            default=50,
            help="Number of container terminal visits to create",
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
        # Create companies
        companies = [CompanyFactory() for _ in range(options["companies"])]
        self.stdout.write(self.style.SUCCESS(f"Created {len(companies)} companies"))

        # Create containers
        containers = [ContainerFactory() for _ in range(options["containers"])]
        self.stdout.write(self.style.SUCCESS(f"Created {len(containers)} containers"))

        # Create container terminal visits
        visits = [
            ContainerTerminalVisitFactory(
                container=containers[i % len(containers)],
                customer=companies[i % len(companies)],
            )
            for i in range(options["visits"])
        ]
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(visits)} container terminal visits")
        )

        # Create container images (optional)
        if options["images"] > 0:
            images = [
                ContainerImageFactory(container=visits[i % len(visits)])
                for i in range(options["images"])
            ]
            self.stdout.write(
                self.style.SUCCESS(f"Created {len(images)} container images")
            )

        # Create container documents (optional)
        if options["documents"] > 0:
            documents = [
                ContainerDocumentFactory(container=visits[i % len(visits)])
                for i in range(options["documents"])
            ]
            self.stdout.write(
                self.style.SUCCESS(f"Created {len(documents)} container documents")
            )

        self.stdout.write(
            self.style.SUCCESS("Test data generation completed successfully")
        )
