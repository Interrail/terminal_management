import pytest
from django.urls import reverse
from rest_framework import status

from apps.core.choices import ContainerType
from apps.core.models import Container


@pytest.mark.django_db
class TestContainerAPI:
    def test_container_list(self, api_client, obtain_jwt_token):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data

    def test_container_create(self, api_client, obtain_jwt_token):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_create")
        print(url)
        data = {"name": "CONT-003", "type": ContainerType.FORTY}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "name" in response.data
        assert response.data["name"] == "CONT-003"

    def test_container_create_duplicate_name(
        self, api_client, obtain_jwt_token, container
    ):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_create")
        data = {"name": container.name, "type": ContainerType.FORTY}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_container_detail(self, api_client, obtain_jwt_token, container):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_detail", kwargs={"container_id": container.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == container.name
        assert response.data["type"] == container.get_type_display()

    def test_container_update(self, api_client, obtain_jwt_token, container):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_update", kwargs={"container_id": container.id})
        data = {"name": "CONT-UPDATED", "type": ContainerType.FORTY}
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "CONT-UPDATED"

    def test_container_delete(self, api_client, obtain_jwt_token, container):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_delete", kwargs={"container_id": container.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Container.objects.filter(id=container.id).exists()

    def test_container_detail_not_found(self, api_client, obtain_jwt_token):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_detail", kwargs={"container_id": 9999999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_container_update_not_found(self, api_client, obtain_jwt_token):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_update", kwargs={"container_id": 9999999})
        data = {"name": "CONT-UPDATED", "type": ContainerType.FORTY}
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_container_delete_not_found(self, api_client, obtain_jwt_token):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("container_delete", kwargs={"container_id": 9999999})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
