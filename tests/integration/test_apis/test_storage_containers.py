from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.containers.models import ContainerStorage
from apps.core.choices import ContainerSize, ContainerState, TransportType
from apps.core.models import Container


@pytest.mark.django_db
class TestContainerStorageRegistration:
    def test_successful_registration(
        self,
        authenticated_api_client,
        company,
        yard,
        contract_service,
        obtain_jwt_token,
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": "CONT1998221",
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            # "container_location": {
            #     "yard_id": yard.id,
            #     "row": 2,
            #     "column_start": 1,
            #     "column_end": 2,
            #     "tier": 1,
            # },
            "company_id": company.id,
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [
                {
                    "id": contract_service.id,
                    "date_from": "2024-01-01",
                    "date_to": "2024-01-09",
                }
            ],
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert ContainerStorage.objects.count() == 1
        assert Container.objects.filter(name="CONT1998221").exists()

    def test_registration_with_container_already_in_storage(
        self,
        container_terminal_visit,
        authenticated_api_client,
        company,
        container,
        container_location,
        yard,
        contract_service,
        obtain_jwt_token,
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": "ABCD1998028",
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            # "container_location": {
            #     "yard_id": yard.id,
            #     "row": 2,
            #     "column_start": 1,
            #     "column_end": 2,
            #     "tier": 1,
            # },
            "company_id": company.id,
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [
                {
                    "id": contract_service.id,
                    "date_from": "2024-01-01",
                    "date_to": "2024-01-09",
                }
            ],
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ContainerStorage.objects.count() == 1
        assert Container.objects.count() == 1  # No new container created

    def test_registration_with_nonexistent_customer(
        self, authenticated_api_client, contract_service, obtain_jwt_token
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": "ABCD1998028",
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            "company_id": 9999999,  # Non-existent customer ID
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [
                {
                    "id": contract_service.id,
                    "date_from": "2024-01-01",
                    "date_to": "2024-01-09",
                }
            ],
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_custom_entry_time(
        self, authenticated_api_client, company, contract_service, obtain_jwt_token
    ):
        url = reverse("container_storage_register")
        custom_time = timezone.now() - timedelta(days=1)
        data = {
            "container_name": "CONT0042445",
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            "company_id": company.id,  # Non-existent customer ID
            "entry_time": custom_time,
            "notes": "Test registration",
            "services": [
                {
                    "id": contract_service.id,
                    "date_from": "2024-01-01",
                    "date_to": "2024-01-09",
                }
            ],
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        storage = ContainerStorage.objects.get(container__name="CONT0042445")
        assert storage.entry_time.isoformat() == custom_time.isoformat()

    def test_registration_with_invalid_container_size(
        self, authenticated_api_client, company, contract_service
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": "CONT0042445",
            "container_size": "12",
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            "company_id": company.id,  # Non-existent customer ID
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [
                {
                    "id": contract_service.id,
                    "date_from": "2024-01-01",
                    "date_to": "2024-01-09",
                }
            ],
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_duplicate_container_name(
        self, authenticated_api_client, company, container, contract_service
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": container.name,
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            "company_id": company.id,  # Non-existent customer ID
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [{"id": contract_service.id}],
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        # Check that the existing container was used, not a new one created
        assert Container.objects.count() == 1
        assert Container.objects.get().size == container.size

    def test_registration_with_missing_required_fields(self, authenticated_api_client):
        url = reverse("container_storage_register")
        data = {
            "container_name": "CONT006",
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "This field is required" in str(response.content)

    def test_registration_output_serializer(
        self, authenticated_api_client, company, container, contract_service
    ):
        url = reverse("container_storage_register")
        data = {
            "container_name": container.name,
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            "company_id": company.id,  # Non-existent customer ID
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [{"id": contract_service.id}],
        }
        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "transport_type" in response.data
        assert "company" in response.data
        assert "container_state" in response.data
        assert "container_owner" in response.data
        assert "notes" in response.data


@pytest.mark.django_db
class TestContainerStorageUpdate:
    def test_successful_update(
        self,
        authenticated_api_client,
        container_terminal_visit,
        container,
        company,
        contract_service,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_name": "UPDATEDNAME",
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            "company_id": company.id,
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [{"id": contract_service.id}],
        }

        # Print initial state

        response = authenticated_api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Refresh the container_terminal_visit from the database
        container_terminal_visit.refresh_from_db()
        container_terminal_visit.container.refresh_from_db()
        # Assertions
        assert (
            container_terminal_visit.container.name == "UPDATEDNAME"
        ), f"Expected UPDATEDNAME, got {container_terminal_visit.container.name}"
        assert container_terminal_visit.container.size == ContainerSize.FORTY
        assert container_terminal_visit.container_state == ContainerState.LOADED

    def test_update_nonexistent_visit(
        self,
        authenticated_api_client,
        container_terminal_visit,
        company,
        container,
        contract_service,
    ):
        url = reverse(
            "container_storage_update",
            kwargs={"visit_id": container_terminal_visit.id + 1},
        )
        data = {
            "container_id": container.id,
            "container_name": "UPDATEDNAME",
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            "company_id": company.id,  # Non-existent customer ID
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [{"id": contract_service.id}],
        }
        response = authenticated_api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_with_invalid_customer_id(
        self,
        authenticated_api_client,
        container_terminal_visit,
        contract_service,
        company,
        container,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_name": "UPDATEDNAME",
            "container_size": ContainerSize.FORTY,
            "container_state": ContainerState.LOADED,
            "container_owner": "Test Owner",
            "product_name": "Test Product",
            "transport_type": TransportType.AUTO,
            "transport_number": "Test Number",
            "company_id": company.id + 9999999,  # Non-existent customer ID
            "entry_time": "2024-01-01",
            "notes": "Test registration",
            "services": [{"id": contract_service.id}],
        }
        response = authenticated_api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_with_invalid_container_name(
        self,
        authenticated_api_client,
        container_terminal_visit,
        container_location,
        container,
        yard,
        company,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": container_terminal_visit.container_location.container.id,
            "container_name": "INVALIDNAMEINVALID",  # Assuming there's validation for container names
            "container_type": ContainerSize.TWENTY,
            "container_location": {
                "yard_id": container_location.yard.id,
                "row": 2,
                "column_start": 1,
                "column_end": 2,
                "tier": 1,
            },
            "company_id": container_terminal_visit.company.id,
            "is_empty": False,
        }
        response = authenticated_api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_with_exit_time_before_entry_time(
        self,
        authenticated_api_client,
        container_terminal_visit,
        container,
        container_location,
        yard,
        company,
    ):
        url = reverse(
            "container_storage_update", kwargs={"visit_id": container_terminal_visit.id}
        )
        data = {
            "container_id": container_terminal_visit.container_location.container.id,
            "container_name": "UPDATEDNAME",
            "container_type": ContainerSize.TWENTY,
            "company_id": container_terminal_visit.company.id,
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
        response = authenticated_api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestContainerStorageDelete:
    def test_successful_delete(
        self, authenticated_api_client, container_terminal_visit
    ):
        url = reverse(
            "container_storage_delete", kwargs={"visit_id": container_terminal_visit.id}
        )
        response = authenticated_api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert ContainerStorage.objects.count() == 0

    def test_invalid_terminal_visit_delete(
        self, authenticated_api_client, container_terminal_visit
    ):
        url = reverse(
            "container_storage_delete",
            kwargs={"visit_id": container_terminal_visit.id + 9999999},
        )
        response = authenticated_api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert ContainerStorage.objects.count() == 1
