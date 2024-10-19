from collections import OrderedDict

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, Q
from rest_framework import serializers
from rest_framework.views import APIView

from ..services.container_storage_finance import ContainerFinanceService
from ...customers.models import ContractService


from rest_framework.response import Response


class ContainerStorageFinanceList(APIView):
    """
    API view to list container storage finances with dynamic service headers and page-based pagination.
    """

    class ContainerSerializer(serializers.Serializer):
        """
        Serializer for Container details.
        """

        name = serializers.CharField(read_only=True)
        size = serializers.CharField(read_only=True)

    class ContainerStorageOutputSerializer(serializers.Serializer):
        """
        Serializer for ContainerStorage with dynamic services.
        """

        id = serializers.IntegerField(read_only=True)
        container = serializers.SerializerMethodField()
        entry_time = serializers.DateTimeField(read_only=True)
        exit_time = serializers.DateTimeField(read_only=True)
        container_state = serializers.CharField(read_only=True)
        services = serializers.SerializerMethodField()

        def get_container(self, obj):
            return {
                "name": obj.container.name,
                "size": obj.container.size,
            }

        def get_services(self, obj):
            """
            Map services for a container to the service names.
            """
            service_names = self.context.get("service_names", [])
            service_mapping = {name: 0 for name in service_names}

            for service_instance in obj.services.all():
                service_name = service_instance.contract_service.service.name
                price = service_instance.contract_service.price
                if service_name in service_mapping:
                    service_mapping[service_name] += float(price)

            return service_mapping

    def get_unique_services(self, queryset):
        """
        Retrieve all unique services across the queryset.
        """
        services = (
            ContractService.objects.filter(
                container_instance_services__container_storage__in=queryset
            )
            .select_related("service__service_type")
            .distinct()
        )

        unique_services_dict = OrderedDict()
        for service in services:
            service_name = service.service.name
            if service_name not in unique_services_dict:
                unique_services_dict[service_name] = {
                    "id": service.service.id,
                    "name": service_name,
                    "service_type": service.service.service_type.name,
                    "unit_of_measure": service.service.service_type.unit_of_measure,
                }

        return list(unique_services_dict.values())

    def get(self, request):
        """
        Handle GET requests to list container storage finances with dynamic headers and page-based pagination.
        """
        page = request.query_params.get("page", 1)
        results_per_page = request.query_params.get("results", 50)
        sort_field = request.query_params.get("sortField")
        sort_order = request.query_params.get("sortOrder")

        container_finance_service = ContainerFinanceService()
        queryset = container_finance_service.get_container_list_finance()

        # Apply sorting
        if sort_field and sort_field.startswith("service_id_"):
            service_id = sort_field.split("_")[-1]
            queryset = queryset.annotate(
                service_price=Sum(
                    "services__contract_service__price",
                    filter=Q(services__contract_service__service_id=service_id),
                )
            )
            order_by = "-service_price" if sort_order == "descend" else "service_price"
            queryset = queryset.order_by(order_by)
        elif sort_field:
            order_by = f"-{sort_field}" if sort_order == "descend" else sort_field
            queryset = queryset.order_by(order_by)
        if request.query_params.get("container_state[]", None):
            queryset = queryset.filter(
                container_state=request.query_params.get("container_state[]")
            )
        if request.query_params.get("entry_time", None):
            entry_time_range = request.query_params.get("entry_time").split("_")
            queryset = queryset.filter(entry_time__range=entry_time_range)
        if request.query_params.get("exit_time", None):
            exit_time_range = request.query_params.get("exit_time").split("_")
            queryset = queryset.filter(exit_time__range=exit_time_range)

        unique_services = self.get_unique_services(queryset)
        service_names = [service["name"] for service in unique_services]

        # Paginate the queryset
        paginator = Paginator(queryset, results_per_page)
        try:
            paginated_qs = paginator.page(page)
        except PageNotAnInteger:
            paginated_qs = paginator.page(1)
        except EmptyPage:
            paginated_qs = paginator.page(paginator.num_pages)

        # Serialize the paginated data
        serializer = self.ContainerStorageOutputSerializer(
            paginated_qs, many=True, context={"service_names": service_names}
        )

        # Prepare the response
        response_data = {
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "results": serializer.data,
            "headers": unique_services,
        }

        return Response(response_data)
