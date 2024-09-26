from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.choices import TransportType, ContainerState
from apps.core.models import BaseModel, Container


class ContainerStorage(BaseModel):
    container = models.ForeignKey(
        Container, on_delete=models.CASCADE, related_name="storages"
    )

    container_location = models.ForeignKey(
        "locations.ContainerLocation",
        on_delete=models.SET_NULL,
        related_name="terminal_visits",
        null=True,
        blank=True,
    )
    container_state = models.CharField(choices=ContainerState.choices, max_length=10)
    company = models.ForeignKey(
        "customers.Company", on_delete=models.CASCADE, related_name="container_visits"
    )
    product_name = models.CharField(max_length=255, blank=True, default="")
    container_owner = models.CharField(max_length=255, blank=True, default="")

    transport_type = models.CharField(
        max_length=255, blank=True, choices=TransportType.choices
    )
    transport_number = models.CharField(max_length=255, blank=True, default="")
    entry_time = models.DateTimeField(default=timezone.now)

    exit_transport_type = models.CharField(
        max_length=255, blank=True, choices=TransportType.choices, null=True
    )
    exit_transport_number = models.CharField(
        max_length=255, blank=True, default="", null=True
    )
    exit_time = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True, default="")
    contract = models.ForeignKey(
        "customers.CompanyContract",
        on_delete=models.SET_NULL,
        related_name="container_visits",
        null=True,
        blank=True,
    )
    active_services = models.ManyToManyField(
        "customers.ContractService", related_name="containers", blank=True
    )
    dispatch_services = models.ManyToManyField(
        "customers.ContractService", related_name="dispatched_containers", blank=True
    )

    class Meta:
        db_table = "container_storage"
        verbose_name = "Container Storage"
        verbose_name_plural = "Container Storages"
        ordering = ["-entry_time"]

    def __str__(self):
        status = "In storage" if self.exit_time is None else "Exited"
        return f" - {self.company.name} - {status} (Entered: {self.entry_time})"

    def clean(self):
        if self.exit_time and self.exit_time < self.entry_time:
            raise ValidationError(_("Exit time must be after entry time."))

    def save(self, *args, **kwargs):
        self.clean()
        if self.container_location:
            self.container = self.container_location.container
        super().save(*args, **kwargs)

    @property
    def current_location(self):
        return self.container_location

    @property
    def storage_days(self):
        return (
            (self.exit_time - self.entry_time).days
            if self.exit_time
            else (timezone.now() - self.entry_time).days + 1
        )


class ContainerImage(BaseModel):
    container = models.ForeignKey(
        ContainerStorage,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="container_images")
    name = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "container_image"
        verbose_name = "Container Image"
        verbose_name_plural = "Container Images"

    def __str__(self):
        return f"- {self.created_at}"


class ContainerDocument(BaseModel):
    container = models.ForeignKey(
        ContainerStorage,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document = models.FileField(upload_to="container_documents")
    name = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "container_document"
        verbose_name = "Container Document"
        verbose_name_plural = "Container Documents"

    def __str__(self):
        return f" - {self.created_at}"
