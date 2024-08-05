import pytest
from django.core.exceptions import ValidationError

from apps.containers.models import Container
from apps.locations.models import Yard, ContainerLocation


class TestContainerLocation:
    @pytest.mark.django_db
    def test_container_location_clean_method(self):
        yard = Yard.objects.create(
            name="Test Yard", max_rows=5, max_columns=10, max_tiers=3
        )
        container = Container.objects.create(
            type=Container.ContainerType.TWENTY, name="CONT-TEST"
        )

        # Missing row
        location = ContainerLocation(
            container=container, yard=yard, column_start=1, column_end=1, tier=1
        )
        with pytest.raises(ValidationError):
            location.clean()

        # Row exceeds yard max_rows
        location = ContainerLocation(
            container=container, yard=yard, row=6, column_start=1, column_end=1, tier=1
        )
        with pytest.raises(ValidationError):
            location.clean()

        # Column exceeds yard max_columns
        location = ContainerLocation(
            container=container, yard=yard, row=1, column_start=1, column_end=11, tier=1
        )
        with pytest.raises(ValidationError):
            location.clean()

        # Tier exceeds yard max_tiers
        location = ContainerLocation(
            container=container, yard=yard, row=1, column_start=1, column_end=1, tier=4
        )
        with pytest.raises(ValidationError):
            location.clean()

        # Valid location
        location = ContainerLocation(
            container=container, yard=yard, row=1, column_start=1, column_end=1, tier=1
        )
        location.clean()  # Should not raise ValidationError
