from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.choices import ContainerSize


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Container(models.Model):
    name = models.CharField(
        max_length=12, unique=True, db_index=True, verbose_name=_("Container Name")
    )
    size = models.CharField(
        max_length=4, choices=ContainerSize.choices, verbose_name=_("Container Type")
    )

    class Meta:
        db_table = "container"
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")

    def __str__(self):
        return f"{self.name} ({self.get_size_display()})"

    @property
    def in_storage(self):
        return self.storages.filter(exit_time__isnull=True).exists()

    @property
    def teu(self):
        size = self.size
        if size == ContainerSize.TWENTY:
            return 1
        else:
            return 2


class TerminalServiceType(BaseModel):
    MEASUREMENT_UNITS = [
        ("container", "container"),
        ("day", "day"),
        ("operation", "Operation"),
        ("piece", "Piece"),
    ]
    name = models.TextField(unique=True)
    unit_of_measure = models.CharField(max_length=50, choices=MEASUREMENT_UNITS)

    class Meta:
        db_table = "terminal_service_type"
        verbose_name = "Terminal Service Type"
        verbose_name_plural = "Terminal Service Types"

    def __str__(self):
        return self.name


class TerminalService(BaseModel):
    CONTAINER_SIZES = [
        ("20", "20 feet"),
        ("40", "40 feet"),
        ("20HC", "20 High Cube feet"),
        ("40HC", "40 High Cube feet"),
        ("45", "45 feet"),
        ("any", "Any size"),
    ]

    CONTAINER_STATES = [
        ("loaded", "Loaded"),
        ("empty", "Empty"),
        ("any", "Any state"),
    ]

    name = models.TextField(unique=True)
    service_type = models.ForeignKey(
        TerminalServiceType,
        on_delete=models.PROTECT,
        related_name="services",
        null=True,
    )
    container_size = models.CharField(
        max_length=50, choices=CONTAINER_SIZES, default="ANY"
    )
    container_state = models.CharField(
        max_length=6, choices=CONTAINER_STATES, default="ANY"
    )
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ["name", "container_size", "container_state"]
        verbose_name = "Terminal Service"
        verbose_name_plural = "Terminal Services"

    def __str__(self):
        return f"{self.name} ({self.get_container_size_display()} - {self.get_container_state_display()})"
