from django.urls import path

from .api import (
    CompanyCreateApi,
    CompanyDetailApi,
    CompanyListApi,
    CompanyUpdateApi,
    CompanyDeleteApi,
)

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
]
