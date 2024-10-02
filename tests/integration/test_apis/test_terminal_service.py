import pytest
from django.urls import reverse
from rest_framework import status

from apps.core.choices import ContainerSize, ContainerState
from apps.core.models import TerminalServiceType, TerminalService


@pytest.mark.django_db
class TestTerminalServiceTypeAPI:
    def test_list_terminal_service_types(self, api_client):
        url = reverse("terminal_service_type_list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_create_terminal_service_type(self, api_client):
        url = reverse("terminal_service_type_create")
        data = {"name": "Test Service Type", "unit_of_measure": "unit"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert TerminalServiceType.objects.filter(name="Test Service Type").exists()

    def test_update_terminal_service_type(self, api_client, terminal_service_type):
        url = reverse(
            "terminal_service_type_update", kwargs={"pk": terminal_service_type.id}
        )
        data = {"name": "Updated Service Type", "unit_of_measure": "updated unit"}
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        terminal_service_type.refresh_from_db()
        assert terminal_service_type.name == "Updated Service Type"

    def test_update_nonexistent_terminal_service_type(self, api_client):
        url = reverse("terminal_service_type_update", kwargs={"pk": 99999})
        data = {"name": "Nonexistent Service Type", "unit_of_measure": "unit"}
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_terminal_service_type(self, api_client, terminal_service_type):
        url = reverse(
            "terminal_service_type_delete", kwargs={"pk": terminal_service_type.id}
        )
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TerminalServiceType.objects.filter(
            id=terminal_service_type.id
        ).exists()

    def test_delete_nonexistent_terminal_service_type(self, api_client):
        url = reverse("terminal_service_type_delete", kwargs={"pk": 99999})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTerminalServiceAPI:
    def test_list_terminal_services(self, api_client):
        url = reverse("terminal_service_list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_create_terminal_service(self, api_client, terminal_service_type):
        url = reverse("terminal_service_create")
        data = {
            "name": "Test Service",
            "service_type_id": terminal_service_type.id,
            "container_size": ContainerSize.TWENTY,
            "container_state": ContainerState.LOADED,
            "base_price": 100,
            "description": "Test Description",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert TerminalService.objects.filter(name="Test Service").exists()

    def test_create_duplicate_terminal_service(self, api_client, terminal_service):
        url = reverse("terminal_service_create")
        data = {
            "name": terminal_service.name,
            "service_type_id": terminal_service.service_type_id,
            "container_size": terminal_service.container_size,
            "container_state": terminal_service.container_state,
            "base_price": terminal_service.base_price,
            "description": "Test Description",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_terminal_service_with_invalid_service_type(self, api_client):
        url = reverse("terminal_service_create")
        data = {
            "name": "Test Service",
            "service_type_id": 99999,
            "container_size": ContainerSize.TWENTY,
            "container_state": ContainerState.LOADED,
            "base_price": 100,
            "description": "Test Description",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_terminal_service_with_invalid_container_size(
        self, api_client, terminal_service_type
    ):
        url = reverse("terminal_service_create")
        data = {
            "name": "Test Service",
            "service_type_id": terminal_service_type.id,
            "container_size": "INVALID",
            "container_state": ContainerState.LOADED,
            "base_price": 100,
            "description": "Test Description",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_terminal_service(self, api_client, terminal_service):
        url = reverse(
            "terminal_service_update", kwargs={"service_id": terminal_service.id}
        )
        data = {
            "name": "Updated Service",
            "service_type_id": terminal_service.service_type_id,
            "container_size": terminal_service.container_size,
            "container_state": terminal_service.container_state,
            "base_price": 200,
            "description": "Updated Description",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        terminal_service.refresh_from_db()
        assert terminal_service.name == "Updated Service"

    def test_update_nonexistent_terminal_service(self, api_client, service_type):
        url = reverse("terminal_service_update", kwargs={"service_id": 99999})
        data = {
            "name": "Nonexistent Service",
            "service_type_id": service_type.id,
            "container_size": ContainerSize.TWENTY,
            "container_state": ContainerState.LOADED,
            "base_price": 100,
            "description": "Test Description",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_terminal_service(self, api_client, terminal_service):
        url = reverse(
            "terminal_service_delete", kwargs={"service_id": terminal_service.id}
        )
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TerminalService.objects.filter(id=terminal_service.id).exists()
