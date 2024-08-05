from django.urls import path

from apps.containers.api import (
    ContainerDeleteApi,
    ContainerUpdateApi,
    ContainerDetailApi,
    ContainerCreateApi,
    ContainerListApi,
    ContainerStorageRegisterApi,
    ContainerStorageListApi,
    ContainerStorageStatisticsApi,
    ContainerStorageUpdateApi,
    ContainerStorageDeleteApi,
    ContainerStorageAddImageListApi,
    ContainerStorageImageDeleteApi,
    ContainerStorageAddDocumentListApi,
    ContainerStorageDocumentDeleteApi,
)

urlpatterns = [
    path("list/", ContainerListApi.as_view(), name="container_list"),
    path("create/", ContainerCreateApi.as_view(), name="container_create"),
    path("<int:container_id>/", ContainerDetailApi.as_view(), name="container_detail"),
    path(
        "<int:container_id>/update/",
        ContainerUpdateApi.as_view(),
        name="container_update",
    ),
    path(
        "<int:container_id>/delete/",
        ContainerDeleteApi.as_view(),
        name="container_delete",
    ),
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
        "container_statistics/",
        ContainerStorageStatisticsApi.as_view(),
        name="container_statistics",
    ),
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
