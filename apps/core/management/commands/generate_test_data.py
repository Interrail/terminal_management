from django.core.management.base import BaseCommand

from apps.customers.factories import CompanyFactory


class Command(BaseCommand):
    help = "Generates test data for Company model"

    def add_arguments(self, parser):
        parser.add_argument(
            "count", type=int, help="Indicates the number of companies to be created"
        )

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        for _ in range(count):
            company = CompanyFactory()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created company: {company.name}")
            )
