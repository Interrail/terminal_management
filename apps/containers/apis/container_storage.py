from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.services.container_storage import (
    ContainerStorageService,
)
from apps.core.choices import ContainerSize, TransportType, ContainerState
from apps.core.models import Container
from apps.core.pagination import LimitOffsetPagination, get_paginated_response
from apps.core.utils import inline_serializer
from apps.customers.models import Company


class ContainerStorageRegisterApi(APIView):

    class ContainerStorageRegisterSerializer(serializers.Serializer):
        container_name = serializers.CharField(max_length=11)
        container_size = serializers.ChoiceField(
            required=True, choices=ContainerSize.choices
        )
        container_state = serializers.ChoiceField(
            required=True, choices=ContainerState.choices
        )
        container_owner = serializers.CharField(required=True, allow_blank=True)
        product_name = serializers.CharField(
            required=True, allow_null=True, allow_blank=True
        )
        transport_type = serializers.ChoiceField(
            required=True, choices=TransportType.choices
        )
        transport_number = serializers.CharField(required=True, allow_blank=True)
        company_id = serializers.IntegerField(required=True)
        entry_time = serializers.DateTimeField(required=True)
        notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        active_services = serializers.ListField(
            child=serializers.IntegerField(),
            required=True,
        )

        def validate_container_size(self, container_size: str) -> str:
            if container_size not in dict(ContainerSize.choices).keys():
                raise serializers.ValidationError("Invalid container size")
            return container_size

        def validate_container_name(self, container_name: str) -> str:
            container = Container.objects.filter(name=container_name).first()
            if container and container.in_storage:
                raise serializers.ValidationError(
                    "Container is already in storage",
                )
            return container_name

        def validate_company_id(self, company_id: int) -> int:
            if not Company.objects.filter(id=company_id).first():
                raise serializers.ValidationError("Customer does not exist")
            return company_id

    class ContainerStorageRegisterOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        container = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "size": serializers.CharField(read_only=True),
            }
        )
        container_state = serializers.CharField(read_only=True)
        transport_type = serializers.CharField(read_only=True)
        transport_number = serializers.CharField(read_only=True)
        product_name = serializers.CharField(read_only=True)
        container_owner = serializers.CharField(read_only=True)

        company = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
            }
        )
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
            serializer.validated_data
        )
        return Response(
            self.ContainerStorageRegisterOutputSerializer(container).data,
            status=status.HTTP_201_CREATED,
        )


class ContainerStorageUpdateApi(APIView):
    permission_classes = [IsAuthenticated]

    class ContainerStorageUpdateSerializer(serializers.Serializer):
        container_name = serializers.CharField(max_length=11, required=True)
        container_size = serializers.ChoiceField(
            choices=ContainerSize.choices, required=True
        )
        container_state = serializers.ChoiceField(
            choices=ContainerState.choices, required=False
        )
        container_owner = serializers.CharField(required=False)
        transport_type = serializers.ChoiceField(
            choices=TransportType.choices, required=False
        )
        product_name = serializers.CharField(
            required=False, allow_blank=True, allow_null=True
        )
        transport_number = serializers.CharField(required=False)
        exit_transport_type = serializers.ChoiceField(
            choices=TransportType.choices, required=False, allow_blank=True
        )
        exit_transport_number = serializers.CharField(
            required=False, allow_blank=True, allow_null=True
        )
        company_id = serializers.IntegerField(required=True)
        entry_time = serializers.DateTimeField(required=False)
        exit_time = serializers.DateTimeField(required=False, allow_null=True)
        notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        available_services = serializers.ListField(
            child=serializers.IntegerField(),
            required=False,
        )
        dispatch_services = serializers.ListField(
            child=serializers.IntegerField(),
            required=False,
        )

        def validate_company_id(self, value):
            if not Company.objects.filter(id=value).exists():
                raise serializers.ValidationError("Customer does not exist")
            return value

    class ContainerStorageUpdateOutputSerializer(serializers.Serializer):
        company = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
            }
        )

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
    permission_classes = [IsAuthenticated]

    class ContainerStorageDeleteSerializer(serializers.Serializer):
        pass

    @extend_schema(
        summary="Delete container visit", responses=ContainerStorageDeleteSerializer
    )
    def delete(self, request, visit_id):
        ContainerStorageService().delete(visit_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContainerStorageListApi(APIView):
    permission_classes = [IsAuthenticated]

    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        types = serializers.CharField(
            required=False,
        )
        company_name = serializers.CharField(required=False)
        container_name = serializers.CharField(required=False)
        container_size = serializers.CharField(required=False)
        container_state = serializers.ChoiceField(
            choices=ContainerState.choices, required=False
        )
        product_name = serializers.CharField(required=False)
        container_owner = serializers.CharField(required=False)
        transport_type = serializers.CharField(required=False)
        transport_number = serializers.CharField(required=False)
        exit_transport_type = serializers.CharField(required=False)
        exit_transport_number = serializers.CharField(required=False)
        active_services = serializers.CharField(required=False)
        dispatch_services = serializers.CharField(required=False)
        exit_time = serializers.CharField(required=False)
        entry_time = serializers.CharField(required=False)
        storage_days = serializers.IntegerField(required=False)
        notes = serializers.CharField(required=False)

    class ContainerStorageListSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        container = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "size": serializers.CharField(
                    source="get_size_display", read_only=True
                ),
            }
        )
        company = inline_serializer(
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
        product_name = serializers.CharField(read_only=True)
        container_owner = serializers.CharField(read_only=True)
        transport_type = serializers.CharField(read_only=True)
        transport_number = serializers.CharField(read_only=True)
        exit_transport_type = serializers.CharField(read_only=True)
        exit_transport_number = serializers.CharField(read_only=True)
        documents = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "document": serializers.FileField(read_only=True),
                "name": serializers.CharField(read_only=True),
            },
            many=True,
        )

        container_state = serializers.CharField(read_only=True)
        entry_time = serializers.DateTimeField(read_only=True)
        exit_time = serializers.DateTimeField(read_only=True)
        storage_days = serializers.IntegerField(read_only=True)
        notes = serializers.CharField(read_only=True)
        free_days = serializers.IntegerField(
            read_only=True, source="contract.free_days"
        )
        active_services = serializers.SerializerMethodField(
            method_name="get_active_services"
        )
        dispatch_services = serializers.SerializerMethodField(
            method_name="get_dispatch_services"
        )

        def get_active_services(self, obj):
            active_services = []
            for service in obj.active_services.all():
                active_services.append(
                    {
                        "id": service.id,
                        "name": service.service.name,
                        "description": service.service.description,
                        "container_size": service.service.container_size,
                        "container_state": service.service.container_state,
                        "service_type": {
                            "id": service.service.service_type.id,
                            "name": service.service.service_type.name,
                            "unit_of_measure": service.service.service_type.unit_of_measure,
                        },
                        "base_price": service.service.base_price,
                        "price": service.price,
                    }
                )
            return active_services

        def get_dispatch_services(self, obj):
            dispatch_services = []
            for service in obj.dispatch_services.all():
                dispatch_services.append(
                    {
                        "id": service.id,
                        "name": service.service.name,
                        "description": service.service.description,
                        "container_size": service.service.container_size,
                        "container_state": service.service.container_state,
                        "service_type": {
                            "id": service.service.service_type.id,
                            "name": service.service.service_type.name,
                            "unit_of_measure": service.service.service_type.unit_of_measure,
                        },
                        "base_price": service.service.base_price,
                        "price": service.price,
                    }
                )
            return dispatch_services

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


class ContainerStorageDetailApi(APIView):
    permission_classes = [IsAuthenticated]

    class ContainerStorageDetailSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        container = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "size": serializers.CharField(read_only=True),
            }
        )
        company = inline_serializer(
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
        product_name = serializers.CharField(read_only=True)
        container_owner = serializers.CharField(read_only=True)
        transport_type = serializers.CharField(read_only=True)
        transport_number = serializers.CharField(read_only=True)
        exit_transport_type = serializers.CharField(read_only=True)
        exit_transport_number = serializers.CharField(read_only=True)
        documents = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "document": serializers.FileField(read_only=True),
                "name": serializers.CharField(read_only=True),
            },
            many=True,
        )

        container_state = serializers.CharField(read_only=True)
        entry_time = serializers.DateTimeField(read_only=True)
        exit_time = serializers.DateTimeField(read_only=True)
        storage_days = serializers.IntegerField(read_only=True)
        notes = serializers.CharField(read_only=True)
        free_days = serializers.IntegerField(
            read_only=True, source="contract.free_days"
        )
        active_services = serializers.SerializerMethodField(
            method_name="get_active_services"
        )
        dispatch_services = serializers.SerializerMethodField(
            method_name="get_dispatch_services"
        )

        def get_active_services(self, obj):
            active_services = []
            for service in obj.active_services.all():
                active_services.append(
                    {
                        "id": service.id,
                        "name": service.service.name,
                        "description": service.service.description,
                        "container_size": service.service.container_size,
                        "container_state": service.service.container_state,
                        "service_type": {
                            "id": service.service.service_type.id,
                            "name": service.service.service_type.name,
                            "unit_of_measure": service.service.service_type.unit_of_measure,
                        },
                        "base_price": service.service.base_price,
                        "price": service.price,
                    }
                )
            return active_services

        def get_dispatch_services(self, obj):
            dispatch_services = []
            for service in obj.dispatch_services.all():
                dispatch_services.append(
                    {
                        "id": service.id,
                        "name": service.service.name,
                        "description": service.service.description,
                        "container_size": service.service.container_size,
                        "container_state": service.service.container_state,
                        "service_type": {
                            "id": service.service.service_type.id,
                            "name": service.service.service_type.name,
                            "unit_of_measure": service.service.service_type.unit_of_measure,
                        },
                        "base_price": service.service.base_price,
                        "price": service.price,
                    }
                )
            return dispatch_services

    @extend_schema(
        summary="Get container visit details",
        responses=ContainerStorageDetailSerializer,
    )
    def get(self, request, visit_id):
        container_storage_service = ContainerStorageService()
        container_storage = container_storage_service.get_container_visit(visit_id)
        return Response(
            self.ContainerStorageDetailSerializer(container_storage).data,
            status=status.HTTP_200_OK,
        )


class ContainerStorageDispatchApi(APIView):
    permission_classes = [IsAuthenticated]

    class ContainerStorageExitSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        exit_time = serializers.DateTimeField(required=True)
        exit_transport_type = serializers.ChoiceField(
            choices=TransportType.choices, required=True
        )
        exit_transport_number = serializers.CharField(required=True)
        dispatch_services = serializers.ListField(
            child=serializers.IntegerField(),
            required=True,
        )

    @extend_schema(
        summary="Dispatch container visit",
        request=ContainerStorageExitSerializer,
    )
    def put(self, request, visit_id):
        serializer = self.ContainerStorageExitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container_storage = ContainerStorageService().dispatch_container_visit(
            visit_id, serializer.validated_data
        )
        return Response(
            ContainerStorageDetailApi.ContainerStorageDetailSerializer(
                container_storage
            ).data,
            status=status.HTTP_200_OK,
        )


class ContainerStorageListByCustomerApi(APIView):
    permission_classes = [IsAuthenticated]

    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        types = serializers.CharField(
            required=False,
        )
        company = serializers.CharField(required=False)
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
        company = inline_serializer(
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
        active_services = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(source="service.name"),
                "service_type": serializers.CharField(
                    source="service.service_type.name"
                ),
                "container_size": serializers.CharField(
                    source="service.container_size"
                ),
                "price": serializers.DecimalField(max_digits=10, decimal_places=2),
            },
            many=True,
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
    def get(self, request, company_id):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        container_storage_service = ContainerStorageService()
        container_storages = (
            container_storage_service.get_all_containers_visits_by_company(
                company_id=company_id, filters=filters_serializer.validated_data
            )
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.ContainerStorageByCustomerListSerializer,
            queryset=container_storages,
            request=request,
            view=self,
        )
