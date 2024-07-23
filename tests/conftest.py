import pytest
from django.urls import reverse

from apps.containers.models import Container
from apps.customers.models import Company
from apps.users.models import CustomUser


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        username="test_user",
        password="test_password",
    )


@pytest.fixture
def obtain_jwt_token(api_client, user):
    url = reverse("token_obtain_pair")
    response = api_client.post(
        url, {"username": "test_user", "password": "test_password"}, format="json"
    )
    return response.data


@pytest.fixture
def container():
    return Container.objects.create(
        name="ABCD19980228", type=Container.ContainerType.TWENTY
    )


@pytest.fixture
def customer():
    return Company.objects.create(name="Test Company", address="Test Address")
