from django.db import transaction
from rest_framework.generics import get_object_or_404

from apps.containers.models import ContainerImage, ContainerDocument, ContainerStorage


class ContainerImageService:
    @transaction.atomic
    def create_image(self, visit_id, image):
        get_object_or_404(ContainerStorage, id=visit_id)
        container_image = ContainerImage.objects.create(
            image=image, container_id=visit_id
        )
        return container_image

    def delete_image(self, image_id):
        image = get_object_or_404(ContainerImage, id=image_id)
        image.delete()

    def get_images(self, visit_id):
        images = ContainerImage.objects.filter(container_id=visit_id)
        return images


class ContainerDocumentService:
    def create_documents(self, visit_id, file):
        get_object_or_404(ContainerStorage, id=visit_id)
        container_document = ContainerDocument.objects.create(
            document=file, container_id=visit_id
        )
        return container_document

    def delete_document(self, document_id):
        document = get_object_or_404(ContainerDocument, id=document_id)
        document.delete()

    def get_documents(self, visit_id):
        documents = ContainerDocument.objects.filter(container_id=visit_id)
        return documents
