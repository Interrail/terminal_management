from django.urls import path, include

from apps.containers.apis.container_storage import (
    ContainerStorageRegisterApi,
    ContainerStorageListApi,
    ContainerStorageUpdateApi,
    ContainerStorageDeleteApi,
    ContainerStorageListByCustomerApi,
)
from apps.containers.apis.container_storage_files import (
    ContainerStorageAddImageListApi,
    ContainerStorageImageDeleteApi,
    ContainerStorageAddDocumentListApi,
    ContainerStorageDocumentDeleteApi,
)

files_patterns = [
    path(
        "container_visit/<int:visit_id>/image/create/",
        ContainerStorageAddImageListApi.as_view(),
        name="container_storage_image",
    ),
    path(
        "container_visit/image/<int:image_id>/delete/",
        ContainerStorageImageDeleteApi.as_view(),
        name="container_storage_image_delete",
    ),
    path(
        "container_visit/<int:visit_id>/document/create/",
        ContainerStorageAddDocumentListApi.as_view(),
        name="container_storage_document",
    ),
    path(
        "container_visit/document/<int:document_id>/delete/",
        ContainerStorageDocumentDeleteApi.as_view(),
        name="container_storage_document_delete",
    ),
]

statistics_patterns = []
urlpatterns = [
    path(
        "container_visit_register/",
        ContainerStorageRegisterApi.as_view(),
        name="container_storage_register",
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
        "container_visit_list/<int:customer_id>/",
        ContainerStorageListByCustomerApi.as_view(),
        name="container_storage_register_by_customer",
    ),
    path("container_statistics/", include(statistics_patterns)),
    path("files/", include(files_patterns)),
]
