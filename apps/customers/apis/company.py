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

    class CompanyUpdateOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        address = serializers.CharField(read_only=True)

    @extend_schema(
        summary="Update company",
        responses=CompanyUpdateOutputSerializer,
        request=CompanyUpdateSerializer,
    )
    def put(self, request, company_id):
        serializer = self.CompanyUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_service = CompanyService()
        company = company_service.update_company(
            company_id, **serializer.validated_data
        )
        result = self.CompanyUpdateOutputSerializer(company).data
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
        containers_count = serializers.IntegerField(read_only=True)
        active_contract = serializers.SerializerMethodField("get_active_contract")

        def get_active_contract(self, obj):
            if hasattr(obj, "active_contract_list") and obj.active_contract_list:
                contract = obj.active_contract_list[0]
                return {
                    "id": contract.id,
                    "name": contract.name,
                    "start_date": contract.start_date,
                    "end_date": contract.end_date,
                }
            return None

    @extend_schema(summary="List companies", responses=CompanyListOutputSerializer)
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
    class CompanyDetailOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        address = serializers.CharField(read_only=True)

    @extend_schema(summary="Get company", responses=CompanyDetailOutputSerializer)
    def get(self, request, company_id):
        company = CompanyService().get_company_by_id(company_id)
        result = self.CompanyDetailOutputSerializer(company).data
        return Response(result, status=status.HTTP_200_OK)


class CompanyDeleteApi(APIView):
    class CompanyDeleteSerializer(serializers.Serializer):
        pass

    @extend_schema(summary="Delete company", responses=CompanyDeleteSerializer)
    def delete(self, request, company_id):
        CompanyService().delete_company(company_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
