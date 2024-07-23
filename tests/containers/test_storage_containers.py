from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.containers.models import Container, ContainerTerminalVisit


@pytest.mark.django_db
def test_successful_registration(api_client, customer):
    url = reverse("container_storage_register")
    data = {
        "container_name": "CONT19982211",
        "container_type": Container.ContainerType.FORTY,
        "customer_id": customer.id,
        "is_empty": True,
        "notes": "Test registration",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert ContainerTerminalVisit.objects.count() == 1
    assert Container.objects.filter(name="CONT19982211").exists()


@pytest.mark.django_db
def test_registration_with_existing_container(api_client, customer, container):
    url = reverse("container_storage_register")
    data = {
        "container_name": container.name,
        "container_type": container.type,
        "customer_id": customer.id,
        "is_empty": False,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert ContainerTerminalVisit.objects.count() == 1
    assert Container.objects.count() == 1  # No new container created


@pytest.mark.django_db
def test_registration_with_container_already_in_storage(
    api_client, customer, container
):
    ContainerTerminalVisit.objects.create(
        container=container, customer=customer, is_empty=True
    )
    url = reverse("container_storage_register")
    data = {
        "container_name": container.name,
        "container_type": container.type,
        "customer_id": customer.id,
        "is_empty": False,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Container is already in storage" in str(response.content)


@pytest.mark.django_db
def test_registration_with_nonexistent_customer(api_client):
    url = reverse("container_storage_register")
    data = {
        "container_name": "CONT00319822",
        "container_type": Container.ContainerType.TWENTY,
        "customer_id": 9999,  # Non-existent customer ID
        "is_empty": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_registration_with_custom_entry_time(api_client, customer):
    url = reverse("container_storage_register")
    custom_time = timezone.now() - timedelta(days=1)
    data = {
        "container_name": "CONT00424455",
        "container_type": Container.ContainerType.FORTY_HIGH_CUBE,
        "customer_id": customer.id,
        "is_empty": False,
        "entry_time": custom_time.isoformat(),
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    storage = ContainerTerminalVisit.objects.get(container__name="CONT00424455")
    assert storage.entry_time.isoformat() == custom_time.isoformat()


@pytest.mark.django_db
def test_registration_with_invalid_container_type(api_client, customer):
    url = reverse("container_storage_register")
    data = {
        "container_name": "CONT00424455",
        "container_type": "INVALID",
        "customer_id": customer.id,
        "is_empty": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "is not a valid choice" in str(response.content)


@pytest.mark.django_db
def test_registration_with_duplicate_container_name(api_client, customer, container):
    url = reverse("container_storage_register")
    data = {
        "container_name": container.name,  # Duplicate name
        "container_type": Container.ContainerType.FORTY,  # Different type
        "customer_id": customer.id,
        "is_empty": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    # Check that the existing container was used, not a new one created
    assert Container.objects.count() == 1
    assert Container.objects.get().type == container.type


@pytest.mark.django_db
def test_registration_with_missing_required_fields(api_client):
    url = reverse("container_storage_register")
    data = {
        "container_name": "CONT006",
        # Missing container_type, customer_id, and is_empty
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "This field is required" in str(response.content)


@pytest.mark.django_db
def test_registration_output_serializer(api_client, customer):
    url = reverse("container_storage_register")
    data = {
        "container_name": "CONT007",
        "container_type": Container.ContainerType.TWENTY,
        "customer_id": customer.id,
        "is_empty": True,
        "notes": "Test notes",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "container" in response.data
    assert "customer" in response.data
    assert "is_empty" in response.data
    assert "entry_time" in response.data
    assert "notes" in response.data
    assert response.data["container"]["name"] == "CONT007"
    assert response.data["container"]["type"] == Container.ContainerType.TWENTY
    assert response.data["customer"]["id"] == customer.id
    assert response.data["is_empty"] is True
    assert response.data["notes"] == "Test notes"
