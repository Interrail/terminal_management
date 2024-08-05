from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.models import Container
from apps.core.pagination import LimitOffsetPagination
from apps.locations.services import YardService


class YardListApi(APIView):
    class FilterSerializer(serializers.Serializer):
        container_name = serializers.CharField(required=False)
        container_types = serializers.ChoiceField(
            choices=Container.ContainerType.choices, required=False
        )
        date = serializers.DateField(required=False)
        customer_name = serializers.CharField(required=False)
        is_empty = serializers.BooleanField(required=False, allow_null=True)
        storage_days = serializers.IntegerField(required=False)
        notes = serializers.CharField(required=False)

    class Pagination(LimitOffsetPagination):
        default_limit = 100
        max_limit = 100

    def get(self, request):
        serializer = self.FilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        yards = YardService().get_all(serializer.validated_data)
        return Response(yards)


class AvailablePlacesApi(APIView):
    class FilterSerializer(serializers.Serializer):
        container_type = serializers.ChoiceField(
            choices=Container.ContainerType.choices, required=True
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="container_type",
                required=True,
                type=OpenApiTypes.STR,
            )
        ]
    )
    def get(self, request):
        serializer = self.FilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        yards = YardService().get_places(serializer.validated_data["container_type"])
        return Response(yards, status=status.HTTP_200_OK)


class YardCreateApi(APIView):
    class YardCreateSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        max_rows = serializers.IntegerField(required=True)
        max_columns = serializers.IntegerField(required=True)
        max_tiers = serializers.IntegerField(required=False, default=10)
        x_coordinate = serializers.FloatField(required=True)
        z_coordinate = serializers.FloatField(required=True)
        rotation_degree = serializers.FloatField(required=False, default=0)

    def post(self, request):
        serializer = self.YardCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        yard = YardService().create(serializer.validated_data)
        return Response(
            self.YardCreateSerializer(yard).data, status=status.HTTP_201_CREATED
        )


class YardUpdateApi(APIView):
    class YardUpdateSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(required=True)
        max_rows = serializers.IntegerField(required=True)
        max_columns = serializers.IntegerField(required=True)
        max_tiers = serializers.IntegerField(required=False, default=10)
        x_coordinate = serializers.FloatField(required=True)
        z_coordinate = serializers.FloatField(required=True)
        rotation_degree = serializers.FloatField(required=False, default=0)

    def put(self, request, pk):
        serializer = self.YardUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        yard = YardService().update(pk, serializer.validated_data)
        return Response(self.YardUpdateSerializer(yard).data, status=status.HTTP_200_OK)
