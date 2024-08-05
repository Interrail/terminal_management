import datetime

from django.utils.dateparse import parse_datetime
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.models import Container
from apps.containers.serializers import (
    StorageStatisticsSerializer,
    CustomerStatisticsSerializer,
    ContainerStatisticsSerializer,
    AllStatisticsSerializer,
)
from apps.containers.services import (
    ContainerService,
    ContainerStorageService,
    ContainerImageService,
    ContainerDocumentService,
)
from apps.core.pagination import LimitOffsetPagination, get_paginated_response
from apps.core.utils import inline_serializer
from apps.customers.models import Company


class ContainerListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        type = serializers.ChoiceField(
            choices=Container.ContainerType.choices, required=False
        )

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
        type = serializers.ChoiceField(choices=Container.ContainerType.choices)

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
        type = serializers.ChoiceField(choices=Container.ContainerType.choices)

    class ContainerUpdateOutputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=12)
        type = serializers.ChoiceField(choices=Container.ContainerType.choices)

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


class ContainerStorageRegisterApi(APIView):
    class ContainerStorageRegisterSerializer(serializers.Serializer):
        container_name = serializers.CharField(max_length=12)
        container_type = serializers.ChoiceField(
            choices=Container.ContainerType.choices
        )
        container_location = inline_serializer(
            fields={
                "yard_id": serializers.IntegerField(),
                "row": serializers.IntegerField(),
                "column_start": serializers.IntegerField(),
                "tier": serializers.IntegerField(),
            }
        )
        customer_id = serializers.IntegerField()
        is_empty = serializers.BooleanField()
        entry_time = serializers.DateTimeField(required=False)
        notes = serializers.CharField(required=False)

        def validate_container_name(self, container_name: str) -> str:
            container = Container.objects.filter(name=container_name).first()
            if container and container.in_storage:
                raise serializers.ValidationError("Container is already in storage")
            return container_name

        def validate_customer_id(self, customer_id: int) -> int:
            if not Company.objects.filter(id=customer_id).first():
                raise serializers.ValidationError("Customer does not exist")
            return customer_id

    class ContainerStorageRegisterOutputSerializer(serializers.Serializer):
        container_location = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(source="yard__name", read_only=True),
                "container": inline_serializer(
                    fields={
                        "id": serializers.IntegerField(read_only=True),
                        "name": serializers.CharField(read_only=True),
                        "type": serializers.CharField(read_only=True),
                    }
                ),
                "row": serializers.IntegerField(read_only=True),
                "column_start": serializers.IntegerField(read_only=True),
                "column_end": serializers.IntegerField(read_only=True),
                "tier": serializers.IntegerField(read_only=True),
            }
        )

        customer = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
            }
        )
        is_empty = serializers.BooleanField(read_only=True)
        entry_time = serializers.DateTimeField(read_only=True)
        notes = serializers.CharField(read_only=True)

    @extend_schema(
        summary="Register container entry",
        request=ContainerStorageRegisterSerializer,
        responses=ContainerStorageRegisterOutputSerializer,
    )
    def post(self, request):
        serializer = self.ContainerStorageRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container = ContainerStorageService().register_container_entry(
            **serializer.validated_data
        )
        return Response(
            self.ContainerStorageRegisterOutputSerializer(container).data,
            status=status.HTTP_201_CREATED,
        )


class ContainerStorageUpdateApi(APIView):
    class ContainerStorageUpdateSerializer(serializers.Serializer):
        container_id = serializers.IntegerField()
        container_name = serializers.CharField(max_length=12)
        container_type = serializers.ChoiceField(
            choices=Container.ContainerType.choices,
        )
        container_location = (
            inline_serializer(
                fields={
                    "yard_id": serializers.IntegerField(),
                    "row": serializers.IntegerField(),
                    "column_start": serializers.IntegerField(),
                    "column_end": serializers.IntegerField(),
                    "tier": serializers.IntegerField(),
                },
            ),
        )
        customer_id = serializers.IntegerField()
        is_empty = serializers.BooleanField()
        entry_time = serializers.DateTimeField(required=False)
        exit_time = serializers.DateTimeField(required=False)
        notes = serializers.CharField(required=False)

        def validate_customer_id(self, customer_id: int) -> int:
            if not Company.objects.filter(id=customer_id).first():
                raise serializers.ValidationError("Customer does not exist")
            return customer_id

        def validate_exit_time(self, exit_time: datetime) -> datetime:
            entry_time = self.initial_data.get("entry_time")

            # Convert entry_time to datetime if it's a string
            if isinstance(entry_time, str):
                entry_time = parse_datetime(entry_time)

            if entry_time and exit_time and exit_time <= entry_time:
                raise serializers.ValidationError("Exit time must be after entry time")

            return exit_time

    class ContainerStorageUpdateOutputSerializer(serializers.Serializer):
        container_location = (
            inline_serializer(
                fields={
                    "yard_id": serializers.IntegerField(),
                    "row": serializers.IntegerField(),
                    "column_start": serializers.IntegerField(),
                    "column_end": serializers.IntegerField(),
                    "tier": serializers.IntegerField(),
                    "container": inline_serializer(
                        fields={
                            "id": serializers.IntegerField(read_only=True),
                            "name": serializers.CharField(read_only=True),
                            "type": serializers.CharField(read_only=True),
                        }
                    ),
                },
            ),
        )
        customer = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
            }
        )
        is_empty = serializers.BooleanField(read_only=True)
        entry_time = serializers.DateTimeField(read_only=True)
        notes = serializers.CharField(read_only=True)

    @extend_schema(
        summary="Update container visit",
        request=ContainerStorageUpdateSerializer,
        responses=ContainerStorageUpdateOutputSerializer,
    )
    def put(self, request, visit_id):
        serializer = self.ContainerStorageUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container_visit = ContainerStorageService().update_container_visit(
            visit_id, serializer.validated_data
        )
        return Response(
            self.ContainerStorageUpdateOutputSerializer(container_visit).data,
            status=status.HTTP_200_OK,
        )


class ContainerStorageDeleteApi(APIView):
    class ContainerStorageDeleteSerializer(serializers.Serializer):
        pass

    @extend_schema(
        summary="Delete container visit", responses=ContainerStorageDeleteSerializer
    )
    def delete(self, request, visit_id):
        ContainerStorageService().delete(visit_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContainerStorageListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        types = serializers.CharField(
            required=False,
        )
        customer = serializers.CharField(required=False)
        is_empty = serializers.BooleanField(required=False, allow_null=True)
        container = serializers.CharField(required=False)
        status = serializers.ChoiceField(
            choices=["in_terminal", "left_terminal", "all"],
            required=False,
            default="all",
        )
        entry_time = serializers.DateField(required=False)
        storage_days = serializers.IntegerField(required=False)
        notes = serializers.CharField(required=False)

    class ContainerStorageListSerializer(serializers.Serializer):
        container = serializers.SerializerMethodField(method_name="get_container")
        customer = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
            }
        )
        images = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "image": serializers.ImageField(read_only=True),
                "name": serializers.CharField(read_only=True),
            },
            many=True,
        )
        documents = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "document": serializers.FileField(read_only=True),
                "name": serializers.CharField(read_only=True),
            },
            many=True,
        )

        is_empty = serializers.BooleanField(read_only=True)
        entry_time = serializers.DateTimeField(read_only=True)
        exit_time = serializers.DateTimeField(read_only=True)
        storage_days = serializers.IntegerField(read_only=True)
        notes = serializers.CharField(read_only=True)

        def get_container(self, obj):
            return {
                "id": obj.container_location.container.id,
                "name": obj.container_location.container.name,
                "type": obj.container_location.container.get_type_display(),
            }

    @extend_schema(
        summary="List container visits",
        responses=ContainerStorageListSerializer,
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                enum=["in_terminal", "left_terminal", "all"],
                default="all",
            )
        ],
    )
    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        container_storages = ContainerStorageService().get_all_containers_visits(
            filters=filters_serializer.validated_data
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.ContainerStorageListSerializer,
            queryset=container_storages,
            request=request,
            view=self,
        )


class ContainerStorageStatisticsApi(APIView):
    class FilterSerializer(serializers.Serializer):
        type = serializers.ChoiceField(
            choices=["storage", "customer", "container", "all"],
            required=False,
            default="all",
        )
        status = serializers.ChoiceField(
            choices=["in_terminal", "left_terminal", "all"],
            required=False,
            default="all",
        )

    @extend_schema(
        summary="Get container storage statistics",
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Type of statistics to retrieve",
                enum=["storage", "customer", "container", "all"],
            )
        ],
        responses={
            200: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        statistics_type = filters_serializer.validated_data.get("type")
        statistics_status = filters_serializer.validated_data.get("status")
        statistics = ContainerStorageService().get_statistics(
            type=statistics_type, status=statistics_status
        )

        if statistics_type == "storage":
            serializer = StorageStatisticsSerializer(data=statistics)
        elif statistics_type == "customer":
            serializer = CustomerStatisticsSerializer(data=statistics)
        elif statistics_type == "container":
            serializer = ContainerStatisticsSerializer(data=statistics)
        else:
            serializer = AllStatisticsSerializer(data=statistics)

        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ContainerStorageAddImageListApi(APIView):
    class ContainerStorageAddImageListSerializer(serializers.Serializer):
        images = serializers.ListField(child=serializers.ImageField())

    class ContainerStorageAddImageListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        images = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "image": serializers.ImageField(read_only=True),
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
