import pytest
from django.urls import reverse
from rest_framework import status

from apps.customers.models import Company


@pytest.mark.django_db
def test_company_create(api_client, obtain_jwt_token):
    access_token = obtain_jwt_token["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    url = reverse("customer_create")
    data = {"name": "Test Company", "address": "123 Test Street"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    assert response.data["name"] == "Test Company"
    assert response.data["address"] == "123 Test Street"


@pytest.mark.django_db
def test_company_update(api_client, obtain_jwt_token):
    company = Company.objects.create(name="Old Name", address="Old Address")
    access_token = obtain_jwt_token["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    url = reverse("customer_update", kwargs={"company_id": company.id})
    data = {"name": "New Name", "address": "New Address"}
    response = api_client.put(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "New Name"
    assert response.data["address"] == "New Address"


@pytest.mark.django_db
def test_company_list(api_client, obtain_jwt_token):
    Company.objects.create(name="Company 1", address="Address 1")
    Company.objects.create(name="Company 2", address="Address 2")
    access_token = obtain_jwt_token["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    url = reverse("customer_list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data
    assert len(response.data["results"]) == 2


@pytest.mark.django_db
def test_company_detail(api_client, obtain_jwt_token):
    company = Company.objects.create(name="Test Company", address="Test Address")
    access_token = obtain_jwt_token["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    url = reverse("customer_list", kwargs={"company_id": company.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Test Company"
    assert response.data["address"] == "Test Address"


@pytest.mark.django_db
def test_company_create_duplicate_name(api_client, obtain_jwt_token):
    Company.objects.create(name="Existing Company", address="Existing Address")
    access_token = obtain_jwt_token["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    url = reverse("customer_create")
    data = {"name": "Existing Company", "address": "New Address"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_company_list_filter(api_client, obtain_jwt_token):
    Company.objects.create(name="ABC Company", address="ABC Address")
    Company.objects.create(name="XYZ Company", address="XYZ Address")
    access_token = obtain_jwt_token["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    url = reverse("customer_list")
    response = api_client.get(url, {"name": "ABC"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "ABC Company"
