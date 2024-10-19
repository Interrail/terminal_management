from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.services.container_storage import ContainerStorageService
from apps.core.utils import inline_serializer


class ContainerStorageServicesApi(APIView):
    class ContainerStorageServicesSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        date_from = serializers.DateField(required=False)
        date_to = serializers.DateField(required=False)
        notes = serializers.CharField(required=False)
        performed_at = serializers.DateTimeField(required=False)
        name = serializers.CharField(
            source="contract_service.service.name", required=False
        )
        service_type = inline_serializer(
            fields={
                "id": serializers.IntegerField(read_only=True),
                "name": serializers.CharField(read_only=True),
                "unit_of_measure": serializers.CharField(read_only=True),
            },
            source="contract_service.service.service_type",
        )
        base_price = serializers.DecimalField(
            source="contract_service.service.base_price",
            max_digits=10,
            decimal_places=2,
            read_only=True,
        )
        price = serializers.DecimalField(
            source="contract_service.price", max_digits=10, decimal_places=2
        )

    def get(self, request, visit_id):
        services = ContainerStorageService().get_services(visit_id)
        return Response(
            self.ContainerStorageServicesSerializer(services, many=True).data
        )


class ContainerStorageServicesCreateApi(APIView):
    class ContainerStorageServicesCreateSerializer(serializers.Serializer):
        date_from = serializers.DateField(required=False)
        date_to = serializers.DateField(required=False, allow_null=True)
        notes = serializers.CharField(required=False)
        service_id = serializers.IntegerField()

    def post(self, request, visit_id):
        serializer = self.ContainerStorageServicesCreateSerializer(
            data=request.data, many=True
        )
        serializer.is_valid(raise_exception=True)
        container_storage_service = ContainerStorageService()
        container_storage_service.create_service_instances(
            visit_id, serializer.validated_data
        )
        return Response(status=status.HTTP_201_CREATED)


class ContainerStorageServiceDeleteApi(APIView):
    def delete(self, request, service_id):
        container_storage_service = ContainerStorageService()
        container_storage_service.delete_service_instance(service_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContainerStorageServiceUpdateApi(APIView):
    class ContainerStorageServiceUpdateSerializer(serializers.Serializer):
        date_from = serializers.DateField(required=False, allow_null=True)
        date_to = serializers.DateField(required=False, allow_null=True)
        notes = serializers.CharField(required=False)
        performed_at = serializers.DateTimeField(required=False)

    class ContainerStorageServiceUpdateOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        date_from = serializers.DateField(read_only=True)
        date_to = serializers.DateField(read_only=True)
        notes = serializers.CharField(read_only=True)
        performed_at = serializers.DateTimeField(read_only=True)

    def put(self, request, service_id):
        serializer = self.ContainerStorageServiceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container_storage_service = ContainerStorageService()
        container_storage_service.update_service_instance(
            service_id, serializer.validated_data
        )
        return Response(
            status=status.HTTP_200_OK,
            data=self.ContainerStorageServiceUpdateOutputSerializer(
                serializer.validated_data
            ).data,
        )
