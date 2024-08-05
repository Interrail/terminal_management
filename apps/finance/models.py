from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.containers.models import Container
from apps.core.models import BaseModel
from apps.customers.models import Company


class CustomerStorageCost(BaseModel):
    customer = models.ForeignKey(
        Company, on_delete=models.SET_NULL, related_name="storage_costs", null=True
    )
    container_type = models.CharField(
        max_length=4,
        choices=Container.ContainerType.choices,
        verbose_name=_("Container Type"),
    )
    is_empty = models.BooleanField(default=False)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ["customer", "container_type", "is_empty"]
        verbose_name = _("Customer Storage Cost")
        verbose_name_plural = _("Customer Storage Costs")

    def __str__(self):
        return f"{self.customer.name} - {self.get_container_type_display()} - {'Empty' if self.is_empty else 'Full'}: {self.daily_rate}/day"
