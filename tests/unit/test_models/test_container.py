import pytest
from django.db import IntegrityError

from apps.containers.models import Container
from apps.locations.models import Yard, ContainerLocation


@pytest.mark.django_db
class TestContainer:
    def test_container_teu_property(self):
        container_20 = Container(type=Container.ContainerType.TWENTY, name="CONT-20")
        container_40 = Container(type=Container.ContainerType.FORTY, name="CONT-40")
        container_40hc = Container(
            type=Container.ContainerType.FORTY_HIGH_CUBE, name="CONT-40HC"
        )
        container_45 = Container(
            type=Container.ContainerType.FORTY_FIVE, name="CONT-45"
        )

        assert container_20.teu == 1
        assert container_40.teu == 2
        assert container_40hc.teu == 2
        assert (
            container_45.teu == 2
        )  # Assuming 45ft is treated as 2 TEU, adjust if different

    def test_container_in_storage_property(self):
        container = Container.objects.create(
            type=Container.ContainerType.TWENTY, name="CONT-TEST"
        )
        yard = Yard.objects.create(
            name="TestYard", max_rows=10, max_columns=10, max_tiers=5
        )

        # Container not in storage
        assert not container.in_storage

        # Add container to yard
        ContainerLocation.objects.create(
            container=container, yard=yard, row=1, column_start=1, column_end=1, tier=1
        )

        # Refresh container from db to update related objects
        container.refresh_from_db()
        assert container.in_storage

    def test_container_unique_name(self):
        Container.objects.create(
            type=Container.ContainerType.TWENTY, name="CONT-UNIQUE"
        )
        with pytest.raises(IntegrityError):
            Container.objects.create(
                type=Container.ContainerType.FORTY, name="CONT-UNIQUE"
            )
