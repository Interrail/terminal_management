from django.core.management import BaseCommand

from apps.core.choices import ContainerSize, ContainerState
from apps.core.models import FreeDayCombination


class Command(BaseCommand):
    help = "Populate FreeDayCombination table with all possible combinations"

    def handle(self, *args, **kwargs):
        container_sizes = ContainerSize.choices  # Define your container sizes
        container_states = ContainerState.choices  # Define your container states
        categories = ["import", "export", "transit"]

        for size in container_sizes:
            for state in container_states:
                for category in categories:
                    FreeDayCombination.objects.get_or_create(
                        container_size=size[0],
                        container_state=state[0],
                        category=category,
                        defaults={"default_free_days": 0},
                    )
        self.stdout.write(self.style.SUCCESS("FreeDayCombination table populated!"))
