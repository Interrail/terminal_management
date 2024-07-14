from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.customers.models import Company


class Container(TimeStampedModel):
    class ContainerType(models.TextChoices):
        TWENTY = "20", _("20 ft Standard")
        TWENTY_HIGH_CUBE = "20H", _("20 ft High Cube")
        FORTY = "40", _("40 ft Standard")
        FORTY_HIGH_CUBE = "40HC", _("40 ft High Cube")
        FORTY_FIVE = "45", _("45 ft High Cube")

    type = models.CharField(
        max_length=4, choices=ContainerType.choices, verbose_name=_("Container Type")
    )
    name = models.CharField(
        max_length=11, unique=True, db_index=True, verbose_name=_("Container Name")
    )

    class Meta:
        db_table = "container"
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class ContainerStorage(TimeStampedModel):
    container = models.ForeignKey(
        Container,
        on_delete=models.CASCADE,
        related_name="container_stays",
    )
    customer = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="containers_stored"
    )
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    storage_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default="")
    is_empty = models.BooleanField(default=False)

    class Meta:
        db_table = "container_storage"
        verbose_name = "Container Storage"
        verbose_name_plural = "Container Storages"
        ordering = ["-entry_time"]

    def __str__(self):
        status = "In storage" if self.exit_time is None else "Exited"
        return f"{self.container.name} - {self.customer.name} - {status} (Entered: {self.entry_time})"

    def save(self, *args, **kwargs):
        if self.exit_time and self.exit_time > self.entry_time:
            self.storage_days = (self.exit_time - self.entry_time).days
        super().save(*args, **kwargs)
