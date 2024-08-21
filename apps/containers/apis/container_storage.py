import datetime

from django.utils.dateparse import parse_datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.services.container_storage import (
    ContainerStorageService,
)
from apps.core.choices import ContainerType
from apps.core.models import Container
from apps.core.pagination import LimitOffsetPagination, get_paginated_response
from apps.core.utils import inline_serializer
from apps.customers.models import Company


class ContainerStorageRegisterApi(APIView):
    class ContainerStorageRegisterSerializer(serializers.Serializer):
        container_name = serializers.CharField(max_length=11)
        container_type = serializers.ChoiceField(choices=ContainerType.choices)
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
        notes = serializers.CharField(required=False, allow_blank=True)

        def validate_container_name(self, container_name: str) -> str:
            container = Container.objects.filter(name=container_name).first()
            if container and container.in_storage:
                raise serializers.ValidationError(
                    "Container is already in storage",
                )
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
            choices=ContainerType.choices,
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
        container = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "type": serializers.CharField(
                    source="get_type_display", read_only=True
                ),
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
        total_storage_cost = serializers.DecimalField(
            max_digits=10, decimal_places=2, read_only=True
        )

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


class ContainerStorageListByCustomerApi(APIView):
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

    class ContainerStorageByCustomerListSerializer(serializers.Serializer):
        container = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "type": serializers.CharField(
                    source="get_type_display", read_only=True
                ),
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
        total_storage_cost = serializers.DecimalField(
            max_digits=10, decimal_places=2, read_only=True
        )

    @extend_schema(
        summary="List container visits",
        responses=ContainerStorageByCustomerListSerializer,
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                enum=["in_terminal", "left_terminal", "all"],
                default="all",
            )
        ],
    )
    def get(self, request, customer_id):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        container_storages = (
            ContainerStorageService().get_all_containers_visits_by_customer(
                customer_id=customer_id, filters=filters_serializer.validated_data
            )
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.ContainerStorageByCustomerListSerializer,
            queryset=container_storages,
            request=request,
            view=self,
        )
