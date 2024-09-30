from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import get_paginated_response, LimitOffsetPagination
from apps.customers.services import (
    CompanyContractService,
    ContractServiceService,
    ContractFreeDayService,
)


class CompanyContractCreateApi(APIView):
    class CompanyContractCreateSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        start_date = serializers.DateField(required=True, allow_null=True)
        end_date = serializers.DateField(required=True, allow_null=True)
        is_active = serializers.BooleanField(required=True)
        free_days = serializers.IntegerField(required=True)
        file = serializers.FileField(required=True)

    def post(self, request, company_id):
        serializer = self.CompanyContractCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_contract_service = CompanyContractService()
        company_contract_service.create_contract(company_id, serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class CompanyContractDetailApi(APIView):
    class CompanyContractDetailSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        start_date = serializers.DateField(read_only=True)
        end_date = serializers.DateField(read_only=True)
        is_active = serializers.BooleanField(read_only=True)
        file = serializers.FileField(read_only=True)
        service_count = serializers.SerializerMethodField("get_service_count")

        def get_service_count(self, obj):
            return obj.services.count()

    def get(self, request, contract_id):
        company_contract_service = CompanyContractService()
        company_contract = company_contract_service.get_by_id(contract_id)

        serializer = self.CompanyContractDetailSerializer(company_contract)

        return Response(serializer.data)


class CompanyContractUpdateApi(APIView):
    class CompanyContractUpdateSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(required=True)
        start_date = serializers.DateField(required=True, allow_null=True)
        end_date = serializers.DateField(required=True, allow_null=True)
        is_active = serializers.BooleanField(required=True)
        file = serializers.FileField(required=False)

    def put(self, request, contract_id):
        serializer = self.CompanyContractUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_contract_service = CompanyContractService()
        contract = company_contract_service.update_contract(
            contract_id, serializer.validated_data
        )

        return Response(
            data=self.CompanyContractUpdateSerializer(contract).data,
            status=status.HTTP_200_OK,
        )


class CompanyContractDeleteApi(APIView):
    def delete(self, request, contract_id):
        company_contract_service = CompanyContractService()
        company_contract_service.delete_contract(contract_id)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyContractByCompanyListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class CompanyContractListSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(read_only=True)
        start_date = serializers.DateField(read_only=True)
        end_date = serializers.DateField(read_only=True)
        is_active = serializers.BooleanField(read_only=True)
        file = serializers.FileField(read_only=True)
        service_count = serializers.SerializerMethodField("get_service_count")

        def get_service_count(self, obj):
            return obj.services.count()

    def get(self, request, company_id):
        company_contract_service = CompanyContractService()
        company_contracts = company_contract_service.get_all_by_company(company_id)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.CompanyContractListSerializer,
            queryset=company_contracts,
            request=request,
            view=self,
        )


class CompanyServiceListByContractApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        container_size = serializers.CharField(required=False)
        container_state = serializers.CharField(required=False)

    class CompanyServicesByContractListSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(source="service.name", read_only=True)
        description = serializers.CharField(
            source="service.description", read_only=True
        )
        service_type = serializers.SerializerMethodField("get_service_type")
        container_size = serializers.CharField(
            source="service.container_size", read_only=True
        )
        container_state = serializers.CharField(
            source="service.container_state", read_only=True
        )
        base_price = serializers.FloatField(source="service.base_price", read_only=True)
        price = serializers.FloatField(read_only=True)

        def get_service_type(self, obj):
            return {
                "id": obj.service.service_type.id,
                "name": obj.service.service_type.name,
                "unit_of_measure": obj.service.service_type.unit_of_measure,
            }

    @extend_schema(
        request=FilterSerializer, responses=CompanyServicesByContractListSerializer
    )
    def get(self, request, contract_id):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        company_contract_service = ContractServiceService()
        company_services = company_contract_service.get_services_by_contract(
            contract_id, filter_serializer.validated_data
        )

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.CompanyServicesByContractListSerializer,
            queryset=company_services,
            request=request,
            view=self,
        )


class CompanyActiveServiceListByCompanyApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        container_size = serializers.CharField(required=False)
        container_state = serializers.CharField(required=False)

    class CompanyActiveServiceListByCompanySerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField(source="service.name", read_only=True)
        description = serializers.CharField(
            source="service.description", read_only=True
        )
        service_type = serializers.SerializerMethodField("get_service_type")
        container_size = serializers.CharField(
            source="service.container_size", read_only=True
        )
        container_state = serializers.CharField(
            source="service.container_state", read_only=True
        )
        base_price = serializers.FloatField(source="service.base_price", read_only=True)
        price = serializers.FloatField(read_only=True)

        def get_service_type(self, obj):
            return {
                "id": obj.service.service_type.id,
                "name": obj.service.service_type.name,
                "unit_of_measure": obj.service.service_type.unit_of_measure,
            }

    @extend_schema(
        request=FilterSerializer, responses=CompanyActiveServiceListByCompanySerializer
    )
    def get(self, request, company_id):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        company_contract_service = ContractServiceService()
        company_services = company_contract_service.get_active_services_by_company(
            company_id, filter_serializer.validated_data
        )

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.CompanyActiveServiceListByCompanySerializer,
            queryset=company_services,
            request=request,
            view=self,
        )


class CompanyServiceUpdateApi(APIView):
    class CompanyServiceUpdateSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        price = serializers.FloatField(required=True, min_value=0)

        def validate_price(self, value):
            if value < 0:
                raise serializers.ValidationError(
                    "Price must be greater than or equal to 0"
                )
            return value

    @extend_schema(request=CompanyServiceUpdateSerializer)
    def put(self, request, contract_id, service_id):
        serializer = self.CompanyServiceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_contract_service = ContractServiceService()
        service = company_contract_service.update_service(
            contract_id, service_id, serializer.validated_data
        )

        return Response(
            data=self.CompanyServiceUpdateSerializer(service).data,
            status=status.HTTP_200_OK,
        )


class ContractFreeDaysListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 100
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        container_size = serializers.CharField(required=False)
        container_state = serializers.CharField(required=False)
        category = serializers.CharField(required=False)
        free_days = serializers.IntegerField(required=False)

    class CompanyFreeDaysListSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        container_size = serializers.CharField(
            source="free_day_combination.container_size", read_only=True
        )
        container_state = serializers.CharField(
            source="free_day_combination.container_state", read_only=True
        )
        category = serializers.CharField(
            source="free_day_combination.category", read_only=True
        )
        free_days = serializers.IntegerField(read_only=True)

    @extend_schema(responses=CompanyFreeDaysListSerializer)
    def get(self, request, contract_id):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        company_contract_service = ContractFreeDayService()
        free_days = company_contract_service.get_free_days_by_contract(
            contract_id, filter_serializer.validated_data
        )
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.CompanyFreeDaysListSerializer,
            queryset=free_days,
            request=request,
            view=self,
        )


class CompanyFreeDaysUpdateApi(APIView):
    class CompanyFreeDaysUpdateSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        free_days = serializers.IntegerField(required=True)

    @extend_schema(request=CompanyFreeDaysUpdateSerializer)
    def put(self, request, contract_id, free_day_id):
        serializer = self.CompanyFreeDaysUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_contract_service = ContractFreeDayService()
        free_day = company_contract_service.update_free_day(
            contract_id, free_day_id, serializer.validated_data
        )

        return Response(
            data=self.CompanyFreeDaysUpdateSerializer(free_day).data,
            status=status.HTTP_200_OK,
        )
