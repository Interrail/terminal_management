from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.containers.filters import ContainerStorageFilter
from apps.containers.models import (
    ContainerStorage,
)
from apps.core.services import ContainerService
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
        container_name,
        container_type,
        container_location,
        customer_id,
        is_empty,
        entry_time=None,
        notes="",
    ):
        container = self.container_service.get_or_create_container(
            container_name, container_type
        )
        if container.in_storage:
            raise ValueError("Container is already in storage")

        customer = self.company_service.get_company_by_id(customer_id)
        entry_time = entry_time or timezone.now()
        container_location = self.location_service.create(container, container_location)
        storage_entry = ContainerStorage.objects.create(
            container=container,
            container_location=container_location,
            customer=customer,
            is_empty=is_empty,
            entry_time=entry_time,
            notes=notes,
        )

        return storage_entry

    def update_container_visit(self, visit_id, data):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        container_data = {
            "name": data.pop("container_name"),
            "type": data.pop("container_type"),
        }

        self.container_service.update_container(
            data.pop("container_id"), container_data
        )

        for key, value in data.items():
            setattr(visit, key, value)
        visit.save()
        return visit

    def get_all_containers_visits(self, filters=None):
        filters = filters or {}

        qs = ContainerStorage.objects.select_related(
            "container", "customer"
        ).prefetch_related("images", "documents")

        status = filters.pop("status", "all")
        if status == "in_terminal":
            qs = qs.filter(exit_time__isnull=True)
        elif status == "left_terminal":
            qs = qs.filter(exit_time__isnull=False)

        return ContainerStorageFilter(filters, queryset=qs).qs

    def get_all_containers_visits_by_customer(self, customer_id, filters=None):
        filters = filters or {}
        qs = ContainerStorage.objects.filter(customer_id=customer_id).select_related(
            "container", "customer", "storage_cost"
        )

        status = filters.pop("status", "all")
        if status == "in_terminal":
            qs = qs.filter(exit_time__isnull=True)
        elif status == "left_terminal":
            qs = qs.filter(exit_time__isnull=False)

        return ContainerStorageFilter(filters, queryset=qs).qs

    def delete(self, visit_id):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        visit.delete()
