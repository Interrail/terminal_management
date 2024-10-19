from django.urls import path

from apps.finance.apis.api import ContainerStorageFinanceList

service_type_patterns = []
urlpatterns = [
    path(
        "container/list/",
        ContainerStorageFinanceList.as_view(),
        name="container_storage_finance_list",
    ),
]
