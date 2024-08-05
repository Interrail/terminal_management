from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.containers.models import ContainerStorage
from apps.customers.models import Company


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
        storage = ContainerStorage.objects.create(
            customer=company, entry_time=timezone.now()
        )
        assert "Test Company" in str(storage)
        assert "In storage" in str(storage)

        storage.exit_time = timezone.now() + timedelta(days=1)
        storage.save()
        assert "Exited" in str(storage)
