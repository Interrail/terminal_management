from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel, SoftDeleteModel
from apps.customers.models import Company


class Container(BaseModel, SoftDeleteModel):
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
        max_length=12, unique=True, db_index=True, verbose_name=_("Container Name")
    )

    @property
    def in_storage(self):
        return self.terminal_visits.filter(exit_time=None).exists()

    class Meta:
        db_table = "container"
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class ContainerTerminalVisit(BaseModel, SoftDeleteModel):
    container = models.ForeignKey(
        Container,
        on_delete=models.CASCADE,
        related_name="terminal_visits",
    )
    customer = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="container_visits"
    )
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    storage_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default="")
    is_empty = models.BooleanField(default=False)

    class Meta:
        db_table = "container_terminal_visit"
        verbose_name = "Container Terminal Visit"
        verbose_name_plural = "Container Terminal Visits"
        ordering = ["-entry_time"]

    def __str__(self):
        status = "In terminal" if self.exit_time is None else "Exited"
        return f"{self.container.name} - {self.customer.name} - {status} (Entered: {self.entry_time})"

    def clean(self):
        super().clean()
        if self.exit_time and self.exit_time <= self.entry_time:
            raise ValidationError(_("Exit time must be after entry time."))

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.exit_time:
            self.storage_days = (self.exit_time - self.entry_time).days
        super().save(*args, **kwargs)


class ContainerImage(BaseModel):
    container = models.ForeignKey(
        ContainerTerminalVisit,
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
        return f"{self.container.container.name} - {self.created_at}"


class ContainerDocument(BaseModel):
    container = models.ForeignKey(
        ContainerTerminalVisit,
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
        return f"{self.container.container.name} - {self.created_at}"
