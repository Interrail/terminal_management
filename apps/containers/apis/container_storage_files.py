from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.services.container_storage_files import (
    ContainerImageService,
    ContainerDocumentService,
)


class ContainerStorageAddImageApi(APIView):
    class ContainerStorageAddImageListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)

    @extend_schema(
        summary="Add images to container visit",
        responses=ContainerStorageAddImageListOutputSerializer,
    )
    def post(self, request, visit_id):
        file = request.FILES.get("file")
        if not file or not file.content_type.startswith("image/"):
            return Response(
                {"error": "An image file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        container_image_service = ContainerImageService()
        container_image = container_image_service.create_image(visit_id, file)
        return Response(
            self.ContainerStorageAddImageListOutputSerializer(container_image).data,
            status=status.HTTP_200_OK,
        )


class ContainerStorageImageDeleteApi(APIView):
    class ContainerStorageImageDeleteSerializer(serializers.Serializer):
        pass

    @extend_schema(
        summary="Delete container image",
        responses=ContainerStorageImageDeleteSerializer,
    )
    def delete(self, request, image_id):
        ContainerImageService().delete_image(image_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContainerStorageAddDocumentApi(APIView):
    class ContainerStorageAddDocumentListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)

    @extend_schema(
        summary="Add documents to container visit",
        responses=ContainerStorageAddDocumentListOutputSerializer,
    )
    def post(self, request, visit_id):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "File is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        container_document = ContainerDocumentService().create_documents(visit_id, file)
        return Response(
            self.ContainerStorageAddDocumentListOutputSerializer(
                container_document
            ).data,
            status=status.HTTP_200_OK,
        )


class ContainerStorageDocumentDeleteApi(APIView):
    class ContainerStorageDocumentDeleteSerializer(serializers.Serializer):
        pass

    @extend_schema(
        summary="Delete container document",
        responses=ContainerStorageDocumentDeleteSerializer,
    )
    def delete(self, request, document_id):
        ContainerDocumentService().delete_document(document_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContainerStorageImageDownloadApi(APIView):
    class ContainerStorageImageDownloadSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        image = serializers.FileField()

    @extend_schema(summary="Download images", responses={200: "Stream of image files"})
    def get(self, request, visit_id):
        container_image_service = ContainerImageService()
        images = container_image_service.get_images(visit_id)
        return Response(
            self.ContainerStorageImageDownloadSerializer(images, many=True).data,
            status=status.HTTP_200_OK,
        )


class ContainerStorageDocumentDownloadApi(APIView):
    class ContainerStorageDocumentDownloadSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        document = serializers.FileField()

    @extend_schema(
        summary="Download documents", responses={200: "Stream of document files"}
    )
    def get(self, request, visit_id):
        container_document_service = ContainerDocumentService()
        documents = container_document_service.get_documents(visit_id)
        return Response(
            self.ContainerStorageDocumentDownloadSerializer(documents, many=True).data,
            status=status.HTTP_200_OK,
        )
