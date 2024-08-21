import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_obtain_jwt_token(obtain_jwt_token):
    assert "access" in obtain_jwt_token
    assert "refresh" in obtain_jwt_token


@pytest.mark.django_db
def test_refresh_jwt_token(api_client, obtain_jwt_token):
    refresh_token = obtain_jwt_token["refresh"]
    url = reverse("token_refresh")
    response = api_client.post(url, {"refresh": refresh_token}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


@pytest.mark.django_db
def test_user_list_access(api_client, obtain_jwt_token):
    access_token = obtain_jwt_token["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    url = reverse("user_list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
