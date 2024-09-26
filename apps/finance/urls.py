from django.urls import path, include

service_type_patterns = []
urlpatterns = [
    path("service_types/", include(service_type_patterns)),
]
