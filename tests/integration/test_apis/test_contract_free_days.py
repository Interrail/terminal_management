import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestContractFreeDaysAPI:
    def test_contract_free_days_list(self, api_client, obtain_jwt_token, contract):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse("contract_free_days_list", kwargs={"contract_id": contract.id})
        response = api_client.get(url)
        assert response.status_code == 200

    def test_contract_free_days_update(
        self, api_client, obtain_jwt_token, contract, contract_free_days
    ):
        access_token = obtain_jwt_token["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = reverse(
            "contract_free_days_update",
            kwargs={
                "contract_id": contract.id,
                "free_day_id": contract_free_days[0].id,
            },
        )
        data = {"free_days": 5}
        response = api_client.put(url, data)
        print(response.data)
        assert response.status_code == 200
