from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.services.container_storage_files import (
    ContainerImageService,
    ContainerDocumentService,
)
from apps.core.utils import inline_serializer


class ContainerStorageAddImageListApi(APIView):
    class ContainerStorageAddImageListSerializer(serializers.Serializer):
        images = serializers.ListField(child=serializers.ImageField())

    class ContainerStorageAddImageListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        images = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "image": serializers.ImageField(read_only=True),
                "name": serializers.CharField(read_only=True),
            },
            many=True,
        )

    @extend_schema(
        summary="Add images to container visit",
        request=ContainerStorageAddImageListSerializer,
        responses=ContainerStorageAddImageListOutputSerializer,
    )
    def post(self, request, visit_id):
        serializer = self.ContainerStorageAddImageListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container_visit = ContainerImageService().create_images(
            visit_id, serializer.validated_data["images"]
        )
        return Response(
            self.ContainerStorageAddImageListOutputSerializer(container_visit).data,
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


class ContainerStorageAddDocumentListApi(APIView):
    class ContainerStorageAddDocumentListSerializer(serializers.Serializer):
        documents = serializers.ListField(child=serializers.FileField())

    class ContainerStorageAddDocumentListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        documents = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "document": serializers.FileField(read_only=True),
            },
            many=True,
        )

    @extend_schema(
        summary="Add documents to container visit",
        request=ContainerStorageAddDocumentListSerializer,
        responses=ContainerStorageAddDocumentListOutputSerializer,
    )
    def post(self, request, visit_id):
        serializer = self.ContainerStorageAddDocumentListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container_visit = ContainerDocumentService().create_documents(
            visit_id, serializer.validated_data["documents"]
        )
        return Response(
            self.ContainerStorageAddDocumentListOutputSerializer(container_visit).data,
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
