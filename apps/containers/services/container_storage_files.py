from django.db import transaction
from rest_framework.generics import get_object_or_404

from apps.containers.models import ContainerStorage, ContainerImage, ContainerDocument


class ContainerImageService:
    @transaction.atomic
    def create_images(self, visit_id, images):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        for image in images:
            visit.images.create(image=image)
        return visit

    def delete_image(self, image_id):
        image = get_object_or_404(ContainerImage, id=image_id)
        image.delete()


class ContainerDocumentService:
    def create_documents(self, visit_id, documents):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        for document in documents:
            visit.documents.create(document=document)
        return visit

    def delete_document(self, document_id):
        document = get_object_or_404(ContainerDocument, id=document_id)
        document.delete()
