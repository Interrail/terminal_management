from django.urls import path, include

from apps.core.apis.container import (
    ContainerListApi,
    ContainerCreateApi,
    ContainerDetailApi,
    ContainerUpdateApi,
    ContainerDeleteApi,
)
from apps.core.apis.terminal_service import (
    TerminalServiceTypeListApi,
    TerminalServiceTypeCreateApi,
    TerminalServiceTypeUpdateApi,
    TerminalServiceTypeDeleteApi,
    TerminalServiceListApi,
    TerminalServiceDetailApi,
    TerminalServiceCreateApi,
    TerminalServiceUpdateApi,
    TerminalServiceDeleteApi,
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
terminal_services_patterns = [
    path("list/", TerminalServiceListApi.as_view(), name="terminal_service_list"),
    path(
        "list/<int:service_id>/",
        TerminalServiceDetailApi.as_view(),
        name="terminal_service_detail",
    ),
    path("create/", TerminalServiceCreateApi.as_view(), name="terminal_service_create"),
    path(
        "update/<int:service_id>/",
        TerminalServiceUpdateApi.as_view(),
        name="terminal_service_update",
    ),
    path(
        "delete/<int:service_id>/",
        TerminalServiceDeleteApi.as_view(),
        name="terminal_service_delete",
    ),
]
terminal_service_types_patterns = [
    path(
        "list/", TerminalServiceTypeListApi.as_view(), name="terminal_service_type_list"
    ),
    path(
        "create/",
        TerminalServiceTypeCreateApi.as_view(),
        name="terminal_service_type_create",
    ),
    path(
        "list/<int:pk>/update/",
        TerminalServiceTypeUpdateApi.as_view(),
        name="terminal_service_type_update",
    ),
    path(
        "list/<int:pk>/delete/",
        TerminalServiceTypeDeleteApi.as_view(),
        name="terminal_service_type_delete",
    ),
]

urlpatterns = [
    path("terminal_services/", include(terminal_services_patterns)),
    path("terminal_service_types/", include(terminal_service_types_patterns)),
    path("containers/", include(containers_patterns)),
]
