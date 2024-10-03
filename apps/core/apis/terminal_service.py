from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.choices import ContainerSize, ContainerState
from apps.core.models import TerminalServiceType, TerminalService
from apps.core.pagination import LimitOffsetPagination, get_paginated_response
from apps.core.services.terminal_service import (
    TerminalServiceService,
    TerminalServiceTypeService,
)
from apps.core.utils import inline_serializer


class TerminalServiceListApi(APIView):
    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        description = serializers.CharField(required=False)
        base_price = serializers.DecimalField(
            required=False, max_digits=20, decimal_places=2
        )
        service_type = serializers.IntegerField(required=False)
        container_size = serializers.CharField(required=False)
        container_state = serializers.CharField(required=False)
        unit_of_measure = serializers.CharField(required=False)

    class ServiceListSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        service_type = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "unit_of_measure": serializers.CharField(),
            },
            required=False,
        )
        container_size = serializers.ChoiceField(
            choices=ContainerSize.choices, read_only=True
        )
        container_state = serializers.ChoiceField(
            choices=ContainerState.choices, read_only=True
        )

        base_price = serializers.FloatField(read_only=True)

    class Pagination(LimitOffsetPagination):
        default_limit = 100
        max_limit = 100

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        terminal_services = TerminalServiceService().get_all(
            filter_serializer.validated_data
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.ServiceListSerializer,
            queryset=terminal_services,
            request=request,
            view=self,
        )


class TerminalServiceDetailApi(APIView):
    class ServiceDetailSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        service_type = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "unit_of_measure": serializers.CharField(),
            },
            required=False,
        )
        container_size = serializers.ChoiceField(
            choices=ContainerSize.choices, read_only=True
        )
        container_state = serializers.ChoiceField(
            choices=ContainerState.choices, read_only=True
        )
        base_price = serializers.FloatField(read_only=True)

    def get(self, request, service_id):
        terminal_service = TerminalServiceService()
        terminal_service = terminal_service.get(service_id)
        return Response(
            self.ServiceDetailSerializer(terminal_service).data,
            status=status.HTTP_200_OK,
        )


class TerminalServiceCreateApi(APIView):
    class ServiceCreateSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField()
        description = serializers.CharField()
        service_type_id = serializers.IntegerField()
        container_size = serializers.ChoiceField(choices=ContainerSize.choices)
        container_state = serializers.ChoiceField(choices=ContainerState.choices)
        base_price = serializers.DecimalField(
            max_digits=12, decimal_places=2, allow_null=True
        )

        def validate_service_type_id(self, value):
            if not TerminalServiceType.objects.filter(id=value).exists():
                raise serializers.ValidationError("Service Type does not exist.")
            return value

    def post(self, request):
        serializer = self.ServiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        terminal_service = TerminalServiceService()
        terminal_service = terminal_service.create(serializer.validated_data)
        return Response(
            self.ServiceCreateSerializer(terminal_service).data,
            status=status.HTTP_201_CREATED,
        )


class TerminalServiceUpdateApi(APIView):
    class ServiceUpdateSerializer(serializers.Serializer):
        name = serializers.CharField()
        description = serializers.CharField()
        service_type_id = serializers.IntegerField()
        container_size = serializers.ChoiceField(
            choices=ContainerSize.choices, read_only=True
        )
        container_state = serializers.ChoiceField(
            choices=ContainerState.choices, read_only=True
        )

        base_price = serializers.DecimalField(
            max_digits=12, decimal_places=2, allow_null=True
        )

        def validate_service_type_id(self, value):
            if not TerminalServiceType.objects.filter(id=value).exists():
                raise serializers.ValidationError("Service Type does not exist.")
            return value

        def validate_name(self, value):
            # Exclude the current instance when checking for uniqueness
            instance_id = self.context.get("instance_id")
            if (
                TerminalService.objects.exclude(id=instance_id)
                .filter(name=value)
                .exists()
            ):
                raise serializers.ValidationError(
                    "Service with this name already exists."
                )
            return value

    class ServiceUpdateOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        description = serializers.CharField(read_only=True)
        service_type = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "unit_of_measure": serializers.CharField(),
            },
            read_only=True,
        )
        container_size = serializers.ChoiceField(
            choices=ContainerSize.choices, read_only=True
        )
        container_state = serializers.ChoiceField(
            choices=ContainerState.choices, read_only=True
        )

        base_price = serializers.FloatField(
            read_only=True,
        )

    def put(self, request, service_id):
        print(request.data)
        serializer = self.ServiceUpdateSerializer(
            data=request.data, context={"instance_id": service_id}
        )
        serializer.is_valid(raise_exception=True)
        terminal_service = TerminalServiceService()
        terminal_service = terminal_service.update(
            service_id, serializer.validated_data
        )
        return Response(
            self.ServiceUpdateOutputSerializer(terminal_service).data,
            status=status.HTTP_200_OK,
        )


class TerminalServiceDeleteApi(APIView):
    def delete(self, request, service_id):
        terminal_service = TerminalServiceService()
        terminal_service.delete(service_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TerminalServiceTypeListApi(APIView):
    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)

    class ServiceListSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        unit_of_measure = serializers.CharField(read_only=True)

    class Pagination(LimitOffsetPagination):
        default_limit = 100
        max_limit = 100

    @extend_schema(responses=ServiceListSerializer)
    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        terminal_service = TerminalServiceTypeService()

        terminal_services = terminal_service.get_all(filter_serializer.validated_data)
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.ServiceListSerializer,
            queryset=terminal_services,
            request=request,
            view=self,
        )


class TerminalServiceTypeCreateApi(APIView):
    class TerminalServiceTypeCreateSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(required=True)
        unit_of_measure = serializers.CharField(required=True)

        def validate_name(self, value):
            if TerminalServiceType.objects.filter(name=value).exists():
                raise serializers.ValidationError(
                    "Service with this name already exists."
                )
            return value

    @extend_schema(
        request=TerminalServiceTypeCreateSerializer,
        responses=TerminalServiceTypeCreateSerializer,
    )
    def post(self, request):
        serializer = self.TerminalServiceTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        terminal_service_type = TerminalServiceTypeService()
        terminal_service_type_response = terminal_service_type.create(
            serializer.validated_data
        )
        return Response(
            self.TerminalServiceTypeCreateSerializer(
                terminal_service_type_response
            ).data,
            status=status.HTTP_201_CREATED,
        )


class TerminalServiceTypeUpdateApi(APIView):
    class TerminalServiceTypeUpdateSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(required=True)
        unit_of_measure = serializers.CharField(required=True)

        def validate_name(self, value):
            # Exclude the current instance when checking for uniqueness
            instance_id = self.context.get("instance_id")
            if (
                TerminalServiceType.objects.exclude(id=instance_id)
                .filter(name=value)
                .exists()
            ):
                raise serializers.ValidationError(
                    "Service with this name already exists."
                )
            return value

    @extend_schema(
        request=TerminalServiceTypeUpdateSerializer,
        responses=TerminalServiceTypeUpdateSerializer,
    )
    def put(self, request, pk):
        serializer = self.TerminalServiceTypeUpdateSerializer(
            data=request.data, context={"instance_id": pk}
        )
        serializer.is_valid(raise_exception=True)
        terminal_service_type = TerminalServiceTypeService()
        terminal_service_type_response = terminal_service_type.update(
            pk, serializer.validated_data
        )
        return Response(
            self.TerminalServiceTypeUpdateSerializer(
                terminal_service_type_response
            ).data,
            status=status.HTTP_200_OK,
        )


class TerminalServiceTypeDeleteApi(APIView):
    class InputSerializer(serializers.Serializer):
        pass

    def delete(self, request, pk):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        terminal_service = TerminalServiceTypeService()
        terminal_service.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
