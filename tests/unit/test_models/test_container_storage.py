from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.containers.models import ContainerStorage
from apps.core.choices import ContainerSize
from apps.core.models import Container
from apps.customers.models import Company
from apps.locations.models import ContainerLocation


class TestContainerStorage:
    @pytest.mark.django_db
    def test_container_storage_clean_method(self):
        storage = ContainerStorage(
            entry_time=timezone.now(), exit_time=timezone.now() - timedelta(hours=1)
        )
        with pytest.raises(ValidationError):
            storage.clean()

    @pytest.mark.django_db
    def test_container_storage_str_method(self):
        company = Company.objects.create(name="Test Company")
        container = Container.objects.create(
            size=ContainerSize.TWENTY, name="CONT-TEST"
        )

        container_location = ContainerLocation.objects.create(
            container=container, row=1, column_start=1, column_end=1, tier=1
        )
        storage = ContainerStorage.objects.create(
            container=container,
            container_location=container_location,
            company=company,
            entry_time=timezone.now(),
        )
        assert "Test Company" in str(storage)
        assert "In storage" in str(storage)

        storage.exit_time = timezone.now() + timedelta(days=1)
        storage.save()
        assert "Exited" in str(storage)
