from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.models import Container
from apps.containers.services import ContainerService, ContainerTerminalVisitService
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


class ContainerTerminalVisitRegisterApi(APIView):
    class ContainerTerminalVisitRegisterSerializer(serializers.Serializer):
        container_name = serializers.CharField(max_length=12)
        container_type = serializers.ChoiceField(
            choices=Container.ContainerType.choices
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

    class ContainerTerminalVisitRegisterOutputSerializer(serializers.Serializer):
        container = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "type": serializers.CharField(read_only=True),
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
        request=ContainerTerminalVisitRegisterSerializer,
        responses=ContainerTerminalVisitRegisterOutputSerializer,
    )
    def post(self, request):
        serializer = self.ContainerTerminalVisitRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container = ContainerTerminalVisitService().register_container_entry(
            **serializer.validated_data
        )
        return Response(
            self.ContainerTerminalVisitRegisterOutputSerializer(container).data,
            status=status.HTTP_201_CREATED,
        )


class ContainerTerminalVisitUpdateApi(APIView):
    class ContainerTerminalVisitUpdateSerializer(serializers.Serializer):
        container_id = serializers.IntegerField()
        customer_id = serializers.IntegerField()
        is_empty = serializers.BooleanField()
        entry_time = serializers.DateTimeField(required=False)
        exit_time = serializers.DateTimeField(required=False)
        notes = serializers.CharField(required=False)

    class ContainerTerminalVisitUpdateOutputSerializer(serializers.Serializer):
        container = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "type": serializers.CharField(read_only=True),
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

    def put(self, request, visit_id):
        serializer = self.ContainerTerminalVisitUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container_visit = ContainerTerminalVisitService().update_container_visit(
            visit_id, serializer.validated_data
        )
        return Response(
            self.ContainerTerminalVisitUpdateOutputSerializer(container_visit).data,
            status=status.HTTP_200_OK,
        )


class ContainerTerminalVisitListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        container = serializers.CharField(required=False)
        types = serializers.CharField(
            required=False,
        )
        customer = serializers.CharField(required=False)
        is_empty = serializers.BooleanField(required=False, allow_null=True)

        status = serializers.ChoiceField(
            choices=["in_storage", "left_storage", "all"], required=False, default="all"
        )

    class ContainerTerminalVisitSerializer(serializers.Serializer):
        container = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "type": serializers.CharField(read_only=True),
            }
        )
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

    @extend_schema(
        summary="List container visits",
        responses=ContainerTerminalVisitSerializer,
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                enum=["in_storage", "left_storage", "all"],
                default="all",
            )
        ],
    )
    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        container_storages = ContainerTerminalVisitService().get_all_containers_visits(
            filters=filters_serializer.validated_data
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.ContainerTerminalVisitSerializer,
            queryset=container_storages,
            request=request,
            view=self,
        )


class ContainerStorageStatisticsApi(APIView):
    class FilterSerializer(serializers.Serializer):
        type = serializers.ChoiceField(
            choices=["storage", "customer", "container"], required=False
        )

    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        statistics = ContainerTerminalVisitService().get_statistics(
            type=filters_serializer.validated_data.get("type")
        )
        return Response(statistics, status=status.HTTP_200_OK)
