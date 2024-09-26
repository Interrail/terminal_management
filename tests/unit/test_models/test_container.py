import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.containers.models import ContainerStorage
from apps.core.choices import ContainerSize
from apps.core.models import Container
from apps.customers.models import Company
from apps.locations.models import Yard, ContainerLocation


@pytest.mark.django_db
class TestContainer:
    def test_container_teu_property(self):
        container_20 = Container(size=ContainerSize.TWENTY, name="CONT-20")
        container_40 = Container(size=ContainerSize.FORTY, name="CONT-40")
        container_40hc = Container(size=ContainerSize.FORTY_HIGH_CUBE, name="CONT-40HC")
        container_45 = Container(size=ContainerSize.FORTY_FIVE, name="CONT-45")

        assert container_20.teu == 1
        assert container_40.teu == 2
        assert container_40hc.teu == 2
        assert (
            container_45.teu == 2
        )  # Assuming 45ft is treated as 2 TEU, adjust if different

    def test_container_in_storage_property(self):
        container = Container.objects.create(
            size=ContainerSize.TWENTY, name="CONT-TEST"
        )
        yard = Yard.objects.create(
            name="TestYard", max_rows=10, max_columns=10, max_tiers=5
        )

        # Container not in storage
        assert not container.in_storage

        # Add container to yard
        container_location = ContainerLocation.objects.create(
            container=container, yard=yard, row=1, column_start=1, column_end=1, tier=1
        )
        company = Company.objects.create(name="Test Company")
        ContainerStorage.objects.create(
            container=container,
            entry_time=timezone.now(),
            container_location=container_location,
            company=company,
        )
        # Refresh container from db to update related objects
        container.refresh_from_db()
        assert container.in_storage

    def test_container_unique_name(self):
        Container.objects.create(size=ContainerSize.TWENTY, name="CONT-UNIQUE")
        with pytest.raises(IntegrityError):
            Container.objects.create(size=ContainerSize.FORTY, name="CONT-UNIQUE")
