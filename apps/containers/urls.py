from django.urls import path

from apps.containers.api import (
    ContainerDeleteApi,
    ContainerUpdateApi,
    ContainerDetailApi,
    ContainerCreateApi,
    ContainerListApi,
    ContainerTerminalVisitRegisterApi,
    ContainerTerminalVisitListApi,
    ContainerStorageStatisticsApi,
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
        ContainerTerminalVisitRegisterApi.as_view(),
        name="container_storage_register",
    ),
    path(
        "containers_visit_list/",
        ContainerTerminalVisitListApi.as_view(),
        name="container_storage_register_by_id",
    ),
    path(
        "container_statistics/",
        ContainerStorageStatisticsApi.as_view(),
        name="container_statistics",
    ),
]
