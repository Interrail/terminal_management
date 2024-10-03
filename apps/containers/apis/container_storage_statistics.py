from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.services.container_storage_statistics import (
    ContainerStorageStatisticsService,
)
from apps.core.utils import inline_serializer


class ContainerStorageStatisticsApi(APIView):
    class ContainerStorageStatisticsSerializer(serializers.Serializer):
        container_by_sizes = inline_serializer(
            fields={
                "container_size": serializers.CharField(),
                "container_count": serializers.IntegerField(),
            },
            many=True,
        )
        total_containers = serializers.IntegerField()
        empty_containers = serializers.IntegerField()
        loaded_containers = serializers.IntegerField()
        total_active_containers = serializers.IntegerField()
        total_dispatched_containers = serializers.IntegerField()
        new_arrived_containers = serializers.IntegerField()
        new_dispatched_containers = serializers.IntegerField()

    @extend_schema(
        summary="Get container storage statistics",
        responses=ContainerStorageStatisticsSerializer,
    )
    def get(self, request, *args, **kwargs):
        container_storage_service = ContainerStorageStatisticsService()
        statistics = container_storage_service.get_container_storage_statistics()
        return Response(self.ContainerStorageStatisticsSerializer(statistics).data)
