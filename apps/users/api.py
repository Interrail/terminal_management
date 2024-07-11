# Create your views here.
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.views import APIView

from apps.core.pagination import LimitOffsetPagination, get_paginated_response
from apps.users.services import UserService


class UserListApi(APIView):
    class FilterSerializer(serializers.Serializer):
        username = serializers.CharField(required=False)
        first_name = serializers.CharField(required=False)
        last_name = serializers.CharField(required=False)
        is_active = serializers.BooleanField(required=False, allow_null=True)
        is_staff = serializers.BooleanField(required=False, allow_null=True)
        is_superuser = serializers.BooleanField(required=False, allow_null=True)

    class UserListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        username = serializers.CharField(read_only=True)
        first_name = serializers.CharField(read_only=True)
        last_name = serializers.CharField(read_only=True)
        is_active = serializers.BooleanField(read_only=True)
        is_staff = serializers.BooleanField(read_only=True)
        is_superuser = serializers.BooleanField(read_only=True)

    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    @extend_schema(
        summary="List users",
        responses=UserListOutputSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name="username", description="Username", type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="first_name", description="First name", type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="last_name", description="Last name", type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="is_active", description="Is active", type=OpenApiTypes.BOOL
            ),
            OpenApiParameter(
                name="is_staff", description="Is staff", type=OpenApiTypes.BOOL
            ),
            OpenApiParameter(
                name="is_superuser", description="Is superuser", type=OpenApiTypes.BOOL
            ),
        ],
    )
    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        users = UserService().get_all(filter_serializer.validated_data)
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.UserListOutputSerializer,
            queryset=users,
            request=request,
            view=self,
        )
