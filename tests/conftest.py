import pytest
from django.urls import reverse

from apps.containers.models import (
    ContainerStorage,
    ContainerDocument,
    ContainerImage,
)
from apps.core.choices import ContainerSize, ContainerState, MeasurementUnit
from apps.core.models import Container, FreeDayCombination
from apps.core.models import TerminalService, TerminalServiceType
from apps.customers.models import (
    Company,
    CompanyContract,
    ContractService,
    ContractFreeDay,
)
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
    return Container.objects.create(name="ABCD1998028", size=ContainerSize.TWENTY)


@pytest.fixture
def company():
    return Company.objects.create(name="Test Company", address="Test Address")


@pytest.fixture
def container_location(container, yard):
    if container.size == ContainerSize.TWENTY:
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
def container_terminal_visit(container, company, container_location):
    return ContainerStorage.objects.create(
        container=container,
        container_location=container_location,
        company=company,
        entry_time="2024-01-01T00:00:00Z",
        container_state=ContainerState.LOADED,
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


@pytest.fixture
def service_type():
    return TerminalServiceType.objects.create(
        name="Test Service Type",
        unit_of_measure=MeasurementUnit.UNIT,
    )


@pytest.fixture
def service(service_type):
    return TerminalService.objects.create(
        name="Test Service",
        service_type=service_type,
        container_size=ContainerSize.TWENTY,
        container_state=ContainerState.LOADED,
        base_price=300,
    )


@pytest.fixture
def contract(company):
    return CompanyContract.objects.create(
        company=company,
        name="Test Contract",
        start_date="2024-01-01",
        end_date="2024-12-31",
        is_active=True,
    )


@pytest.fixture
def contract_service(contract, service):
    return ContractService.objects.create(
        contract=contract,
        service=service,
        price=50,
    )


@pytest.fixture
def terminal_service_type():
    return TerminalServiceType.objects.create(
        name="Test Service Type",
        unit_of_measure=MeasurementUnit.UNIT,
    )


@pytest.fixture
def terminal_service(terminal_service_type):
    return TerminalService.objects.create(
        name="Test Service",
        service_type=terminal_service_type,
        container_size=ContainerSize.TWENTY,
        container_state=ContainerState.LOADED,
        base_price=100,
    )


@pytest.fixture
def free_day_combination():
    container_sizes = ContainerSize.choices  # Define your container sizes
    container_states = ContainerState.choices  # Define your container states
    categories = ["import", "export", "transit"]
    for size in container_sizes:
        for state in container_states:
            for category in categories:
                FreeDayCombination.objects.get_or_create(
                    container_size=size[0],
                    container_state=state[0],
                    category=category,
                    defaults={"default_free_days": 0},
                )


@pytest.fixture
def contract_free_days(contract, free_day_combination):
    free_day_combinations = FreeDayCombination.objects.all()
    for combination in free_day_combinations:
        ContractFreeDay.objects.get_or_create(
            contract=contract,
            free_day_combination=combination,
            defaults={"free_days": combination.default_free_days},
        )
    return ContractFreeDay.objects.all()
