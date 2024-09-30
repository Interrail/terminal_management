from django.urls import path, include

from apps.customers.apis.company import (
    CompanyCreateApi,
    CompanyDetailApi,
    CompanyListApi,
    CompanyUpdateApi,
    CompanyDeleteApi,
)
from apps.customers.apis.company_contract import (
    CompanyContractCreateApi,
    CompanyContractByCompanyListApi,
    CompanyServiceListByContractApi,
    CompanyContractUpdateApi,
    CompanyContractDeleteApi,
    CompanyServiceUpdateApi,
    CompanyContractDetailApi,
    CompanyActiveServiceListByCompanyApi,
    ContractFreeDaysListApi,
    CompanyFreeDaysUpdateApi,
)

contract_patterns = [
    path(
        "create/<int:company_id>/",
        CompanyContractCreateApi.as_view(),
        name="company_contract_create",
    ),
    path(
        "list/by_company/<int:company_id>/",
        CompanyContractByCompanyListApi.as_view(),
        name="company_contract_list",
    ),
    path(
        "list/<int:contract_id>/",
        CompanyContractDetailApi.as_view(),
        name="company_contract_detail",
    ),
    path(
        "list/update/<int:contract_id>/",
        CompanyContractUpdateApi.as_view(),
        name="company_contract_update",
    ),
    path(
        "list/delete/<int:contract_id>/",
        CompanyContractDeleteApi.as_view(),
        name="company_contract_delete",
    ),
    path(
        "services/<int:contract_id>/",
        CompanyServiceListByContractApi.as_view(),
        name="company_contract_list",
    ),
    path(
        "services/by_company/active/<int:company_id>/",
        CompanyActiveServiceListByCompanyApi.as_view(),
        name="by_company_contract_list",
    ),
    path(
        "<int:contract_id>/services/update/<int:service_id>/",
        CompanyServiceUpdateApi.as_view(),
        name="company_contract_update",
    ),
    path(
        "<int:contract_id>/free_days/list/",
        ContractFreeDaysListApi.as_view(),
        name="contract_free_days_list",
    ),
    path(
        "<int:contract_id>/free_days/<int:free_day_id>/update/",
        CompanyFreeDaysUpdateApi.as_view(),
        name="contract_free_days_update",
    ),
]

urlpatterns = [
    path("create/", CompanyCreateApi.as_view(), name="customer_create"),
    path(
        "update/<int:company_id>/", CompanyUpdateApi.as_view(), name="customer_update"
    ),
    path("list/<int:company_id>/", CompanyDetailApi.as_view(), name="customer_list"),
    path("list/", CompanyListApi.as_view(), name="customer_list"),
    path(
        "<int:company_id>/delete/", CompanyDeleteApi.as_view(), name="customer_delete"
    ),
    path("contracts/", include(contract_patterns)),
]
