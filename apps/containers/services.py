from datetime import timedelta

from django.db import transaction
from django.db.models import ExpressionWrapper, Avg, F, DurationField, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.containers.filters import ContainerStorageFilter
from apps.containers.models import (
    Container,
    ContainerStorage,
    ContainerImage,
    ContainerDocument,
)
from apps.customers.services import CompanyService
from apps.locations.services import ContainerLocationService


class ContainerService:
    def get_all_containers(self):
        return Container.objects.all()

    def create_container(self, data):
        return Container.objects.create(**data)

    def get_or_create_container(self, container_name, container_type):
        if container := Container.objects.filter(name=container_name).first():
            return container
        else:
            return Container.objects.create(name=container_name, type=container_type)

    def get_container(self, container_id):
        return get_object_or_404(Container, id=container_id)

    def get_container_by_name(self, container_name):
        return get_object_or_404(Container, name=container_name)

    def update_container(self, container_id, data):
        container = self.get_container(container_id)
        for key, value in data.items():
            setattr(container, key, value)
        container.save()
        return container

    def delete_container(self, container_id):
        container = self.get_container(container_id)
        container.delete()


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
            "container_location__container", "customer"
        ).prefetch_related("images", "documents")
        status = filters.pop("status", "all")
        if status == "in_terminal":
            qs = qs.filter(exit_time__isnull=True)
        elif status == "left_terminal":
            qs = qs.filter(exit_time__isnull=False)

        return ContainerStorageFilter(filters, queryset=qs).qs

    @staticmethod
    def get_container_types(status=None):
        if status == "in_terminal":
            return list(
                ContainerStorage.objects.filter(exit_time__isnull=True)
                .annotate(type=F("container__type"))
                .values("type")
                .annotate(count=Count("container__type"))
                .order_by("-count")
            )
        elif status == "left_terminal":
            return list(
                ContainerStorage.objects.filter(exit_time__isnull=False)
                .annotate(type=F("container__type"))
                .values("type")
                .annotate(count=Count("container__type"))
                .order_by("-count")
            )
        else:
            return list(
                ContainerStorage.objects.annotate(
                    type=F("container_location__container__type")
                )
                .values("type")
                .annotate(count=Count("container_location__container__type"))
                .order_by("-count")
            )

    @staticmethod
    def get_busiest_customers():
        return list(
            ContainerStorage.objects.annotate(customer_name=F("customer__name"))
            .values("customer_name")
            .annotate(visit_count=Count("id"))
            .order_by("-visit_count")[:8]
        )

    @staticmethod
    def get_storage_statistics():
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Perform a single query to get multiple statistics
        visit_stats = ContainerStorage.objects.aggregate(
            total_containers=Count("id"),
            empty_containers=Count("id", filter=Q(is_empty=True)),
            laden_containers=Count("id", filter=Q(is_empty=False)),
            avg_duration=Avg(
                ExpressionWrapper(
                    F("exit_time") - F("entry_time"), output_field=DurationField()
                ),
                filter=Q(exit_time__isnull=False),
            ),
            entries_30_days=Count("id", filter=Q(entry_time__gte=thirty_days_ago)),
            exits_30_days=Count("id", filter=Q(exit_time__gte=thirty_days_ago)),
        )

        avg_storage_days = (
            visit_stats["avg_duration"].days if visit_stats["avg_duration"] else 0
        )
        turnover_rate = (
            visit_stats["entries_30_days"] + visit_stats["exits_30_days"]
        ) / 30

        MAX_CAPACITY = 60  # Replace with actual capacity
        storage_utilization = (
            (visit_stats["total_containers"] / MAX_CAPACITY) * 100
            if MAX_CAPACITY > 0
            else 0
        )

        return {
            "total_containers": visit_stats["total_containers"],
            "empty_containers": visit_stats["empty_containers"],
            "laden_containers": visit_stats["laden_containers"],
            "avg_storage_days": avg_storage_days,
            "turnover_rate": round(turnover_rate, 2),
            "storage_utilization": round(storage_utilization, 2),
        }

    @classmethod
    def get_statistics(cls, type=None, status=None):
        if type == "container":
            return {"common_types": cls.get_container_types(status)}
        elif type == "customer":
            return {"busiest_customers": cls.get_busiest_customers()}
        elif type == "storage":
            return cls.get_storage_statistics()
        else:
            return {
                "storage": cls.get_storage_statistics(),
                "common_types": cls.get_container_types(status),
                "busiest_customers": cls.get_busiest_customers(),
            }

    def delete(self, visit_id):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        visit.delete()


class ContainerImageService:
    @transaction.atomic
    def create_images(self, visit_id, images):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        for image in images:
            visit.images.create(image=image)
        return visit

    def delete_image(self, image_id):
        image = get_object_or_404(ContainerImage, id=image_id)
        image.delete()


class ContainerDocumentService:
    def create_documents(self, visit_id, documents):
        visit = get_object_or_404(ContainerStorage, id=visit_id)
        for document in documents:
            visit.documents.create(document=document)
        return visit

    def delete_document(self, document_id):
        document = get_object_or_404(ContainerDocument, id=document_id)
        document.delete()
