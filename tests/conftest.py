import pytest
from django.urls import reverse

from apps.containers.models import (
    ContainerStorage,
    ContainerDocument,
    ContainerImage,
)
from apps.core.models import Container
from apps.core.choices import ContainerType
from apps.customers.models import Company
from apps.locations.models import Yard, ContainerLocation
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
def yard():
    return Yard.objects.create(
        name="Test Yard",
        max_rows=10,
        max_columns=4,
        max_tiers=10,
        x_coordinate=0,
        z_coordinate=0,
        rotation_degree=0,
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
    return Container.objects.create(name="ABCD1998028", type=ContainerType.TWENTY)


@pytest.fixture
def customer():
    return Company.objects.create(name="Test Company", address="Test Address")


@pytest.fixture
def container_location(container, yard):
    if container.type == ContainerType.TWENTY:
        return ContainerLocation.objects.create(
            container=container,
            yard=yard,
            row=1,
            column_start=1,
            column_end=1,
            tier=1,
        )
    else:
        return ContainerLocation.objects.create(
            container=container,
            yard=yard,
            row=1,
            column_start=1,
            column_end=2,
            tier=1,
        )


@pytest.fixture
def container_terminal_visit(container, customer, container_location):
    return ContainerStorage.objects.create(
        container=container,
        container_location=container_location,
        customer=customer,
        entry_time="2024-01-01T00:00:00Z",
        is_empty=False,
    )


@pytest.fixture
def container_document(container_terminal_visit):
    return ContainerDocument.objects.create(
        name="Test Document", container=container_terminal_visit
    )


@pytest.fixture
def container_image(container_terminal_visit):
    return ContainerImage.objects.create(
        image="test_image.jpg", container=container_terminal_visit
    )
