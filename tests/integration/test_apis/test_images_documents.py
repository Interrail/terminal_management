import io

import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status


def create_test_image(name="test.png"):
    file = io.BytesIO()
    image = Image.new("RGB", size=(100, 100), color=(255, 0, 0))
    image.save(file, "png")
    file.name = name
    file.seek(0)
    return file


def create_test_document(name="test.pdf"):
    file = io.BytesIO()
    file.write(b"%PDF-1.0\nThis is a test PDF file\n%%EOF")
    file.name = name
    file.seek(0)
    return file


@pytest.mark.django_db
class TestContainerStorageImageAPI:
    def test_add_images_to_visit(self, api_client, container_terminal_visit):
        url = reverse(
            "container_storage_image", kwargs={"visit_id": container_terminal_visit.id}
        )
        image1 = SimpleUploadedFile(
            "test_image1.png", create_test_image().getvalue(), content_type="image/png"
        )
        data = {"file": image1}
        response = api_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_200_OK
        assert "id" in response.data

    def test_add_images_to_nonexistent_visit(self, api_client):
        url = reverse("container_storage_image", kwargs={"visit_id": 99999})
        image = SimpleUploadedFile(
            "test_image.png", create_test_image().getvalue(), content_type="image/png"
        )
        data = {"file": image}
        response = api_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_invalid_file_type_as_image(self, api_client, container_terminal_visit):
        url = reverse(
            "container_storage_image", kwargs={"visit_id": container_terminal_visit.id}
        )
        invalid_file = SimpleUploadedFile(
            "test_file.txt", b"This is not an image", content_type="text/plain"
        )
        data = {"file": invalid_file}
        response = api_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_image(self, api_client, container_image):
        url = reverse(
            "container_storage_image_delete", kwargs={"image_id": container_image.id}
        )
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_nonexistent_image(self, api_client):
        url = reverse("container_storage_image_delete", kwargs={"image_id": 99999})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestContainerStorageDocumentAPI:
    def test_add_document_to_visit(self, api_client, container_terminal_visit):
        url = reverse(
            "container_storage_document_create",
            kwargs={"visit_id": container_terminal_visit.id},
        )
        doc1 = SimpleUploadedFile(
            "test_doc1.pdf",
            create_test_document().getvalue(),
            content_type="application/pdf",
        )
        data = {"file": doc1}
        response = api_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_200_OK

    def test_add_documents_to_nonexistent_visit(self, api_client):
        url = reverse("container_storage_document_create", kwargs={"visit_id": 999999})
        doc = SimpleUploadedFile(
            "test_doc.pdf",
            create_test_document().getvalue(),
            content_type="application/pdf",
        )
        data = {"file": doc}
        response = api_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_document(self, api_client, container_document):
        url = reverse(
            "container_storage_document_delete",
            kwargs={"document_id": container_document.id},
        )
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_nonexistent_document(self, api_client):
        url = reverse(
            "container_storage_document_delete", kwargs={"document_id": 99999}
        )
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
