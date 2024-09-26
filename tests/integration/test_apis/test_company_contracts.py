import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from terminal_management import settings


@pytest.mark.django_db
class TestCompanyContractAPI:
    def test_company_contract_create(
        self, api_client, obtain_jwt_token, company, service
    ):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        data = {
            "name": "Test Contract22",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "is_active": True,
            "file": SimpleUploadedFile("temp_file.txt", b"Temporary file content"),
        }
        url = reverse("company_contract_create", kwargs={"company_id": company.id})
        response = api_client.post(url, data, format="multipart")
        file_path = os.path.join(settings.MEDIA_ROOT, "contracts/temp_file.txt")
        if os.path.exists(file_path):
            os.remove(file_path)
        assert response.status_code == 201

    def test_company_contract_update(
        self, api_client, obtain_jwt_token, company, service, contract
    ):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        data = {
            "name": "Test Contract22",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "is_active": True,
            "file": SimpleUploadedFile("temp_file.txt", b"Temporary file content"),
        }
        url = reverse("company_contract_update", kwargs={"contract_id": contract.id})
        response = api_client.put(url, data, format="multipart")
        file_path = os.path.join(settings.MEDIA_ROOT, "contracts/temp_file.txt")
        if os.path.exists(file_path):
            os.remove(file_path)
        assert response.status_code == 200

    def test_company_contract_delete(
        self, api_client, obtain_jwt_token, company, service, contract
    ):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("company_contract_delete", kwargs={"contract_id": contract.id})
        response = api_client.delete(url)
        assert response.status_code == 204
