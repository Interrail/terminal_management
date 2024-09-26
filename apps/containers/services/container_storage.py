from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.containers.filters import ContainerStorageFilter
from apps.containers.models import (
    ContainerStorage,
)
from apps.core.services.container import ContainerService
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
        entry_time = data["entry_time"]
        storage_entry = ContainerStorage.objects.create(
            container=container,
            company=company,
            container_owner=data["container_owner"],
            product_name=data.get("product_name", ""),
            transport_type=data["transport_type"],
            transport_number=data["transport_number"],
            container_state=data["container_state"],
            entry_time=entry_time,
            notes=data.get("notes", ""),
        )
        storage_entry.active_services.set(data.get("active_services", []))

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

        # Print debug information
        print(f"Updated container: name={container.name}, size={container.size}")

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
        visit.dispatch_services.set(data.get("dispatch_services", []))
        visit.save()
        return visit

    def delete(self, visit_id):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        visit.delete()
