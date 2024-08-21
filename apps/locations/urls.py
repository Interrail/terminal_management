from django.urls import path

from apps.locations.api import (
    YardListApi,
    YardCreateApi,
    YardUpdateApi,
    AvailablePlacesApi,
)

urlpatterns = [
    path("yards/", YardListApi.as_view(), name="yard-list"),
    path("available_places/", AvailablePlacesApi.as_view(), name="yard-list"),
    path("yard/create/", YardCreateApi.as_view(), name="yard-structure"),
    path("yard/<int:pk>/update/", YardUpdateApi.as_view(), name="yard-update"),
]
