from rest_framework.generics import get_object_or_404

from apps.core.filters import TerminalServiceFilter, TerminalServiceTypeFilter
from apps.core.models import TerminalService, TerminalServiceType


class TerminalServiceService:
    def get_all(self, filters=None):
        filters = filters or {}
        qs = TerminalService.objects.all().order_by("-id")
        return TerminalServiceFilter(filters, queryset=qs).qs

    def get(self, service_id):
        return get_object_or_404(TerminalService, id=service_id)

    def create(self, data):
        return TerminalService.objects.create(**data)

    def update(self, service_id, data):
        service = get_object_or_404(TerminalService, id=service_id)
        for key, value in data.items():
            setattr(service, key, value)
        service.save()
        return service

    def delete(self, service_id):
        service = TerminalService.objects.get(id=service_id)
        service.delete()


class TerminalServiceTypeService:
    def get_all(self, filters=None):
        filters = filters or {}
        qs = TerminalServiceType.objects.all()
        return TerminalServiceTypeFilter(filters, queryset=qs).qs

    def create(self, data):
        return TerminalServiceType.objects.create(**data)

    def update(self, service_type_id, data):
        service_type = get_object_or_404(TerminalServiceType, id=service_type_id)
        for key, value in data.items():
            setattr(service_type, key, value)
        service_type.save()
        return service_type

    def delete(self, service_type_id):
        service_type = get_object_or_404(TerminalServiceType, id=service_type_id)
        service_type.delete()
