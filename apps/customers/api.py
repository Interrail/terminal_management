from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import LimitOffsetPagination, get_paginated_response
from apps.customers.services import CompanyService


class CompanyCreateApi(APIView):
    class CompanyCreateSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        address = serializers.CharField(required=True)

        def validate_name(self, value):
            if CompanyService().get_company_by_name(value):
                raise serializers.ValidationError(
                    "Company with this name already exists"
                )
            return value

    class CompanyOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        address = serializers.CharField(read_only=True)

    @extend_schema(
        summary="Create company",
        responses=CompanyOutputSerializer,
        request=CompanyCreateSerializer,
    )
    def post(self, request):
        serializer = self.CompanyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_service = CompanyService()
        company = company_service.create_company(**serializer.validated_data)

        result = self.CompanyOutputSerializer(company).data
        return Response(result, status=status.HTTP_201_CREATED)


class CompanyUpdateApi(APIView):
    class CompanyUpdateSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        address = serializers.CharField(required=False)

    class CompanyOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        address = serializers.CharField(read_only=True)

    def put(self, request, company_id):
        serializer = self.CompanyUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_service = CompanyService()
        company = company_service.update_company(
            company_id, **serializer.validated_data
        )
        result = self.CompanyOutputSerializer(company).data
        return Response(result, status=status.HTTP_200_OK)


class CompanyListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        address = serializers.CharField(required=False)

    class CompanyListOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        address = serializers.CharField(read_only=True)

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        companies = CompanyService().get_all_companies(
            filters=filter_serializer.validated_data
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.CompanyListOutputSerializer,
            queryset=companies,
            request=request,
            view=self,
        )


class CompanyDetailApi(APIView):
    class CompanyOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        address = serializers.CharField(read_only=True)

    def get(self, request, company_id):
        company = CompanyService().get_company_by_id(company_id)
        result = self.CompanyOutputSerializer(company).data
        return Response(result, status=status.HTTP_200_OK)
