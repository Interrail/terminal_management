from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.choices import ContainerType
from apps.core.pagination import LimitOffsetPagination, get_paginated_response
from apps.core.services import ContainerService


class ContainerListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        type = serializers.ChoiceField(choices=ContainerType.choices, required=False)

    class ContainerListSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        type = serializers.CharField(read_only=True, source="get_type_display")

    @extend_schema(summary="List containers", responses=ContainerListSerializer)
    def get(self, request):
        containers = ContainerService().get_all_containers()
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.ContainerListSerializer,
            queryset=containers,
            request=request,
            view=self,
        )


class ContainerCreateApi(APIView):
    class ContainerCreateSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=11)
        type = serializers.ChoiceField(choices=ContainerType.choices)

        def validate_name(self, value):
            if ContainerService().exists_container(value):
                raise serializers.ValidationError(
                    "Container with this name already exists"
                )
            return value

    @extend_schema(
        summary="Create container",
        responses={"name": str},
        request=ContainerCreateSerializer,
    )
    def post(self, request):
        serializer = self.ContainerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container = ContainerService().create_container(serializer.validated_data)

        return Response({"name": container.name}, status=201)


class ContainerDetailApi(APIView):
    class ContainerDetailSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        type = serializers.CharField(read_only=True, source="get_type_display")

    @extend_schema(summary="Get container detail", responses=ContainerDetailSerializer)
    def get(self, request, container_id):
        container = ContainerService().get_container(container_id)

        return Response(
            self.ContainerDetailSerializer(container).data, status=status.HTTP_200_OK
        )


class ContainerUpdateApi(APIView):
    class ContainerUpdateSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=12)
        type = serializers.ChoiceField(choices=ContainerType.choices)

    class ContainerUpdateOutputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=12)
        type = serializers.ChoiceField(choices=ContainerType.choices)

    @extend_schema(
        summary="Update container",
        responses=ContainerUpdateOutputSerializer,
        request=ContainerUpdateSerializer,
    )
    def put(self, request, container_id):
        serializer = self.ContainerUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container = ContainerService().update_container(
            container_id, serializer.validated_data
        )
        return Response({"name": container.name}, status=status.HTTP_200_OK)


class ContainerDeleteApi(APIView):
    class ContainerDeleteSerializer(serializers.Serializer):
        pass

    @extend_schema(summary="Delete container", responses=ContainerDeleteSerializer)
    def delete(self, request, container_id):
        ContainerService().delete_container(container_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
