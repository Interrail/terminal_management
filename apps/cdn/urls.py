from django.urls import path

from apps.cdn.api import UploadFileApi


urlpatterns = [
    path("", UploadFileApi.as_view(), name="upload_file"),
]
