from django.urls import path, include

from apps.containers.apis.container_storage import (
    ContainerStorageRegisterApi,
    ContainerStorageListApi,
    ContainerStorageUpdateApi,
    ContainerStorageDeleteApi,
    ContainerStorageListByCustomerApi,
    ContainerStorageDetailApi,
    ContainerStorageDispatchApi,
    ContainerStorageAvailableServicesApi,
    ContainerStorageRegisterBatchApi,
)
from apps.containers.apis.container_storage_files import (
    ContainerStorageAddImageApi,
    ContainerStorageImageDeleteApi,
    ContainerStorageAddDocumentApi,
    ContainerStorageDocumentDeleteApi,
    ContainerStorageImageDownloadApi,
    ContainerStorageDocumentDownloadApi,
)
from apps.containers.apis.container_storage_report import ContainerStorageReportAPI
from apps.containers.apis.container_storage_service import (
    ContainerStorageServicesApi,
    ContainerStorageServicesCreateApi,
    ContainerStorageServiceDeleteApi,
    ContainerStorageServiceUpdateApi,
)
from apps.containers.apis.container_storage_statistics import (
    ContainerStorageStatisticsApi,
)

files_patterns = [
    path(
        "container_visit/<int:visit_id>/image/create/",
        ContainerStorageAddImageApi.as_view(),
        name="container_storage_image",
    ),
    path(
        "container_visit/image/<int:image_id>/delete/",
        ContainerStorageImageDeleteApi.as_view(),
        name="container_storage_image_delete",
    ),
    path(
        "container_visit/<int:visit_id>/document/create/",
        ContainerStorageAddDocumentApi.as_view(),
        name="container_storage_document_create",
    ),
    path(
        "container_visit/document/<int:document_id>/delete/",
        ContainerStorageDocumentDeleteApi.as_view(),
        name="container_storage_document_delete",
    ),
    path(
        "container_visit/<int:visit_id>/images/download/",
        ContainerStorageImageDownloadApi.as_view(),
        name="container_storage_document",
    ),
    path(
        "container_visit/<int:visit_id>/documents/download/",
        ContainerStorageDocumentDownloadApi.as_view(),
        name="container_storage_document",
    ),
]

statistics_patterns = [
    path(
        "",
        ContainerStorageStatisticsApi.as_view(),
        name="container_storage_register_by_id",
    ),
]
report_patterns = [
    path(
        "<company_id>/",
        ContainerStorageReportAPI.as_view(),
        name="container_storage_report",
    ),
]
urlpatterns = [
    path("report/", include(report_patterns)),
    path(
        "container_visit_register/",
        ContainerStorageRegisterApi.as_view(),
        name="container_storage_register",
    ),
    path(
        "container_visit_register_batch/",
        ContainerStorageRegisterBatchApi.as_view(),
        name="container_storage_register_batch",
    ),
    path(
        "container_visit/<int:visit_id>/available_services/",
        ContainerStorageAvailableServicesApi.as_view(),
        name="container_storage_available_services",
    ),
    path(
        "container_visit/<int:visit_id>/dispatch/",
        ContainerStorageDispatchApi.as_view(),
        name="container_storage_register_by_id",
    ),
    path(
        "container_visit/<int:visit_id>/update/",
        ContainerStorageUpdateApi.as_view(),
        name="container_storage_update",
    ),
    path(
        "container_visit/<int:visit_id>/delete/",
        ContainerStorageDeleteApi.as_view(),
        name="container_storage_delete",
    ),
    path(
        "containers_visit_list/",
        ContainerStorageListApi.as_view(),
        name="container_storage_register_by_id",
    ),
    path(
        "container_visit_list/<int:visit_id>/",
        ContainerStorageDetailApi.as_view(),
        name="container_storage_register_by_customer",
    ),
    path(
        "container_visit_list/by_company/<int:company_id>/",
        ContainerStorageListByCustomerApi.as_view(),
        name="container_storage_register_by_customer",
    ),
    path(
        "container_visit/services/<int:visit_id>/",
        ContainerStorageServicesApi.as_view(),
        name="container_storage_services",
    ),
    path(
        "container_visit/<int:visit_id>/services/create/",
        ContainerStorageServicesCreateApi.as_view(),
        name="container_storage_services_create",
    ),
    path(
        "container_visit/services/<int:service_id>/delete/",
        ContainerStorageServiceDeleteApi.as_view(),
        name="container_storage_services_delete",
    ),
    path(
        "container_visit/services/<int:service_id>/update/",
        ContainerStorageServiceUpdateApi.as_view(),
        name="container_storage_services_update",
    ),
    path("container_visit_statistics/", include(statistics_patterns)),
    path("files/", include(files_patterns)),
]
