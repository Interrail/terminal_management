from django.urls import path, include

from apps.core.api import (
    ContainerListApi,
    ContainerCreateApi,
    ContainerDetailApi,
    ContainerUpdateApi,
    ContainerDeleteApi,
)

containers_patterns = [
    path("create/", ContainerCreateApi.as_view(), name="container_create"),
    path("list/", ContainerListApi.as_view(), name="container_list"),
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
]


urlpatterns = [
    path("containers/", include(containers_patterns)),
]
