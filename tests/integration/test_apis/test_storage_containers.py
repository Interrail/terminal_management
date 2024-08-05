from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.containers.models import Container, ContainerStorage


@pytest.mark.django_db
class TestContainerStorageRegistration:
    def test_successful_registration(self, api_client, customer, yard):
        url = reverse("container_storage_register")
        data = {
            "container_name": "CONT19982211",
            "container_type": Container.ContainerType.FORTY,
            "container_location": {
                "yard_id": yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": customer.id,
            "is_empty": True,
            "notes": "Test registration",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert ContainerStorage.objects.count() == 1
        assert Container.objects.filter(name="CONT19982211").exists()

    def test_registration_with_existing_container(
        self,
        container_terminal_visit,
        api_client,
        customer,
        container,
        container_location,
        yard,
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": container.name,
            "container_type": container.type,
            "container_location": {
                "yard_id": yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": customer.id,
            "is_empty": True,
            "notes": "Test registration",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ContainerStorage.objects.count() == 1
        assert Container.objects.count() == 1  # No new container created

    def test_registration_with_container_already_in_storage(
        self, api_client, customer, container, container_location, yard
    ):
        ContainerStorage.objects.create(
            container_location=container_location, customer=customer, is_empty=True
        )
        url = reverse("container_storage_register")
        data = {
            "container_name": container.name,
            "container_type": container.type,
            "container_location": {
                "yard_id": yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": customer.id,
            "is_empty": False,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Container is already in storage" in str(response.content)

    def test_registration_with_nonexistent_customer(
        self, api_client, container_location, yard
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": "CONT00319822",
            "container_type": Container.ContainerType.TWENTY,
            "container_location": {
                "yard_id": yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": 9999,
            "is_empty": True,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_custom_entry_time(self, api_client, customer, yard):
        url = reverse("container_storage_register")
        custom_time = timezone.now() - timedelta(days=1)
        data = {
            "container_name": "CONT00424455",
            "container_type": Container.ContainerType.FORTY_HIGH_CUBE,
            "container_location": {
                "yard_id": yard.id,
                "row": 2,
                "column_start": 2,
                "column_end": 3,
                "tier": 1,
            },
            "customer_id": customer.id,
            "is_empty": False,
            "entry_time": custom_time.isoformat(),
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        storage = ContainerStorage.objects.get(
            container_location__container__name="CONT00424455"
        )
        assert storage.entry_time.isoformat() == custom_time.isoformat()

    def test_registration_with_invalid_container_type(self, api_client, customer, yard):
        url = reverse("container_storage_register")
        data = {
            "container_name": "CONT00424455",
            "container_type": "INVALID",
            "container_location": {
                "yard_id": yard.id,
                "row": 2,
                "column_start": 2,
                "column_end": 3,
                "tier": 1,
            },
            "customer_id": customer.id,
            "is_empty": True,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "is not a valid choice" in str(response.content)

    def test_registration_with_duplicate_container_name(
        self, api_client, customer, container, yard
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": container.name,  # Duplicate name
            "container_type": Container.ContainerType.FORTY,  # Different type
            "container_location": {
                "yard_id": yard.id,
                "row": 1,
                "column_start": 1,
                "column_end": 2,
                "tier": 2,
            },
            "customer_id": customer.id,
            "is_empty": True,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        # Check that the existing container was used, not a new one created
        assert Container.objects.count() == 1
        assert Container.objects.get().type == container.type

    def test_registration_with_missing_required_fields(self, api_client):
        url = reverse("container_storage_register")
        data = {
            "container_name": "CONT006",
            # Missing container_type, customer_id, and is_empty
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This field is required" in str(response.content)

    def test_registration_output_serializer(self, api_client, customer, yard):
        url = reverse("container_storage_register")
        data = {
            "container_name": "CONT007",
            "container_type": Container.ContainerType.TWENTY,
            "container_location": {
                "yard_id": yard.id,
                "row": 3,
                "column_start": 2,
                "column_end": 3,
                "tier": 1,
            },
            "customer_id": customer.id,
            "is_empty": True,
            "notes": "Test notes",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "container_location" in response.data
        assert "customer" in response.data
        assert "is_empty" in response.data
        assert "entry_time" in response.data
        assert "notes" in response.data
        assert response.data["container_location"]["container"]["name"] == "CONT007"
        assert (
            response.data["container_location"]["container"]["type"]
            == Container.ContainerType.TWENTY
        )
        assert response.data["customer"]["id"] == customer.id
        assert response.data["is_empty"] is True
        assert response.data["notes"] == "Test notes"


@pytest.mark.django_db
class TestContainerStorageUpdate:
    def test_successful_update(
        self,
        api_client,
        container_terminal_visit,
        container_location,
        container,
        customer,
        yard,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": container_terminal_visit.container_location.container.id,
            "container_name": "UPDATEDNAME",
            "container_type": Container.ContainerType.TWENTY,
            "container_location": {
                "yard_id": container_location.yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": container_terminal_visit.customer.id,
            "is_empty": False,
            "notes": "Updated notes",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        container_terminal_visit.refresh_from_db()
        assert (
            container_terminal_visit.container_location.container.name == "UPDATEDNAME"
        )
        assert (
            container_terminal_visit.container_location.container.type
            == Container.ContainerType.TWENTY
        )
        assert not container_terminal_visit.is_empty
        assert container_terminal_visit.notes == "Updated notes"

    def test_update_nonexistent_visit(
        self, api_client, container_location, yard, container_terminal_visit
    ):
        url = reverse(
            "container_storage_update",
            kwargs={"visit_id": container_terminal_visit.id + 1},
        )
        data = {
            "container_id": 1,
            "container_name": "TESTCONT",
            "container_type": Container.ContainerType.FORTY,
            "container_location": {
                "yard_id": container_location.yard.id,
                "row": 4,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": 1,
            "is_empty": True,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_with_invalid_container_id(
        self, api_client, container_terminal_visit, container_location, yard, customer
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": 99999,  # Non-existent container ID
            "container_name": "UPDATEDNAME",
            "container_type": Container.ContainerType.TWENTY,
            "container_location": {
                "yard_id": container_location.yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": container_terminal_visit.customer.id,
            "is_empty": False,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_with_invalid_customer_id(
        self, api_client, container_terminal_visit, container_location, yard, container
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": container_terminal_visit.container_location.container.id,
            "container_name": "UPDATEDNAME",
            "container_type": Container.ContainerType.TWENTY,
            "container_location": {
                "yard_id": container_location.yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": 99999,  # Non-existent customer ID
            "is_empty": False,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_with_invalid_container_name(
        self,
        api_client,
        container_terminal_visit,
        container_location,
        customer,
        container,
        yard,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": container_terminal_visit.container_location.container.id,
            "container_name": "INVALIDNAMEINVALID",  # Assuming there's validation for container names
            "container_type": Container.ContainerType.TWENTY,
            "container_location": {
                "yard_id": container_location.yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "customer_id": container_terminal_visit.customer.id,
            "is_empty": False,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_with_exit_time_before_entry_time(
        self,
        api_client,
        container_terminal_visit,
        container,
        customer,
        container_location,
        yard,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": container_terminal_visit.container_location.container.id,
            "container_name": "UPDATEDNAME",
            "container_type": Container.ContainerType.TWENTY,
            "customer_id": container_terminal_visit.customer.id,
            "container_location": {
                "yard_id": container_location.yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "is_empty": False,
            "entry_time": timezone.now(),
            "exit_time": timezone.now()
            - timezone.timedelta(hours=1),  # Exit time before entry time
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_with_partial_data(
        self,
        api_client,
        container_terminal_visit,
        container_location,
        container,
        customer,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": container_terminal_visit.container_location.container.id,
            "container_name": "UPDATEDNAME",
            "container_type": Container.ContainerType.TWENTY,
            "customer_id": container_terminal_visit.customer.id,
            "is_empty": False,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        container_terminal_visit.refresh_from_db()
        assert (
            container_terminal_visit.container_location.container.name == "UPDATEDNAME"
        )
        assert not container_terminal_visit.is_empty

    def test_update_with_same_data(
        self,
        api_client,
        container_terminal_visit,
        container_location,
        container,
        customer,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": container_terminal_visit.container_location.container.id,
            "container_name": container_terminal_visit.container_location.container.name,
            "container_type": container_terminal_visit.container_location.container.type,
            "customer_id": container_terminal_visit.customer.id,
            "is_empty": container_terminal_visit.is_empty,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        # Check that no actual changes were made
        container_terminal_visit.refresh_from_db()
        assert (
            container_terminal_visit.container_location.container.name
            == data["container_name"]
        )
        assert container_terminal_visit.is_empty == data["is_empty"]


@pytest.mark.django_db
class TestContainerStorageDelete:
    def test_successful_delete(self, api_client, container_terminal_visit):
        url = reverse(
            "container_storage_delete", kwargs={"visit_id": container_terminal_visit.id}
        )
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert ContainerStorage.objects.count() == 0

    def test_invalid_terminal_visit_delete(self, api_client, container_terminal_visit):
        url = reverse(
            "container_storage_delete",
            kwargs={"visit_id": container_terminal_visit.id + 999},
        )
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert ContainerStorage.objects.count() == 1
