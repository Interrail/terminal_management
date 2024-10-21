from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.containers.filters import ContainerStorageFilter
from apps.containers.models import (
    ContainerStorage,
    ContainerServiceInstance,
)
from apps.core.services.container import ContainerService
from apps.customers.models import ContractService
from apps.customers.services import CompanyService
from apps.locations.services import ContainerLocationService


class ContainerStorageService:
    def __init__(self):
        self.container_service = ContainerService()
        self.company_service = CompanyService()
        self.location_service = ContainerLocationService()

    @transaction.atomic
    def register_container_entry(
        self,
        data,
    ):
        container = self.container_service.get_or_create_container(
            data["container_name"], data["container_size"]
        )
        if container.in_storage:
            raise ValueError("Container is already in storage")
        company = self.company_service.get_company_by_id(data["company_id"])
        storage_entry = self._create_storage_entry(data, container, company)
        self._create_service_instances(storage_entry, data.pop("services", []))

        return storage_entry

    def update_container_visit(self, visit_id, data):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        available_services = data.pop("available_services", [])
        dispatch_services = data.pop("dispatch_services", [])
        container_name = data.pop("container_name")
        container_size = data.pop("container_size")

        # Update the existing container
        container = visit.container
        container.name = container_name
        container.size = container_size
        container.save()

        for key, value in data.items():
            setattr(visit, key, value)

        visit.active_services.set(available_services)
        visit.dispatch_services.set(dispatch_services)
        visit.save()

        # Print debug information
        print(
            f"Updated visit: container_name={visit.container.name}, container_size={visit.container.size}"
        )

        return visit

    def get_all_containers_visits(self, filters=None):
        filters = filters or {}

        qs = ContainerStorage.objects.select_related(
            "container", "company"
        ).prefetch_related(
            "images",
            "documents",
            "active_services__service__service_type",
            "dispatch_services__service__service_type",
        )

        status = filters.pop("status", "all")
        if status == "in_terminal":
            qs = qs.filter(exit_time__isnull=True)
        elif status == "left_terminal":
            qs = qs.filter(exit_time__isnull=False)

        return ContainerStorageFilter(filters, queryset=qs).qs

    def get_all_containers_visits_by_company(self, company_id, filters=None):
        filters = filters or {}
        qs = ContainerStorage.objects.filter(company_id=company_id).select_related(
            "container", "company"
        )

        status = filters.pop("status", "all")
        if status == "in_terminal":
            qs = qs.filter(exit_time__isnull=True)
        elif status == "left_terminal":
            qs = qs.filter(exit_time__isnull=False)

        return ContainerStorageFilter(filters, queryset=qs).qs

    def get_container_visit(self, visit_id):
        return get_object_or_404(ContainerStorage, id=visit_id)

    def dispatch_container_visit(self, visit_id, data):
        visit = self.get_container_visit(visit_id)
        visit.exit_time = data.get("exit_time")
        visit.exit_transport_type = data.get("exit_transport_type")
        visit.exit_transport_number = data.get("exit_transport_number")
        visit.save()
        return visit

    def delete(self, visit_id):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        visit.delete()

    def get_services(self, visit_id):
        visit = self.get_container_visit(visit_id)

        return ContainerServiceInstance.objects.filter(container_storage=visit)

    def get_available_services(self, visit_id):
        visit = self.get_container_visit(visit_id)
        active_contract = visit.company.contracts.filter(is_active=True).first()

        container_services = ContractService.objects.filter(
            container_instance_services__container_storage=visit,
        )
        services_for_one_time = container_services.filter(
            service__multiple_usage=False
        ).values_list("id", flat=True)

        services = (
            ContractService.objects.exclude(id__in=services_for_one_time)
            .filter(
                contract=active_contract,
                service__container_size=visit.container.size,
                service__container_state=visit.container_state,
            )
            .distinct()
        )

        return services

    def create_service_instances(self, visit_id, services):
        visit = self.get_container_visit(visit_id)
        self._create_service_instances(visit, services)

    def delete_service_instance(self, service_id):
        service = get_object_or_404(ContainerServiceInstance, id=service_id)
        service.delete()

    def update_service_instance(self, service_id, data):
        service = get_object_or_404(ContainerServiceInstance, id=service_id)
        for key, value in data.items():
            setattr(service, key, value)
        service.save()
        return service

    def _create_storage_entry(self, data, container, company):
        return ContainerStorage.objects.create(
            container=container,
            company=company,
            container_owner=data["container_owner"],
            product_name=data.get("product_name", ""),
            transport_type=data["transport_type"],
            transport_number=data["transport_number"],
            container_state=data["container_state"],
            entry_time=data["entry_time"],
            notes=data.get("notes", ""),
        )

    def _create_service_instances(self, storage_entry, services):
        for service in services:
            ContainerServiceInstance.objects.create(
                contract_service_id=service.pop("id"),
                container_storage=storage_entry,
                date_from=service.pop("date_from", None),
                date_to=service.pop("date_to", None),
            )
