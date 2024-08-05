from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.containers.models import Container
from apps.core.models import BaseModel


class Yard(BaseModel):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Yard Name"))
    max_rows = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    max_columns = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    max_tiers = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    x_coordinate = models.FloatField(blank=True, null=True)
    z_coordinate = models.FloatField(blank=True, null=True)
    rotation_degree = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "yard"
        verbose_name = _("Yard")
        verbose_name_plural = _("Yards")

    @property
    def total_capacity(self):
        return self.max_rows * self.max_columns * self.max_tiers

    def __str__(self):
        return f"{self.name} ({self.max_rows}x{self.max_columns}x{self.max_tiers})"


class ContainerLocation(BaseModel):
    container = models.ForeignKey(
        Container,
        on_delete=models.CASCADE,
        related_name="locations",
        verbose_name=_("Container"),
    )
    yard = models.ForeignKey(
        Yard,
        on_delete=models.CASCADE,
        related_name="container_locations",
        verbose_name=_("Yard"),
        null=True,
        blank=True,
    )
    row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=True, blank=True
    )
    column_start = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=True, blank=True
    )
    column_end = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=True, blank=True
    )
    tier = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=True, blank=True
    )

    class Meta:
        db_table = "container_location"
        verbose_name = _("Container Location")
        verbose_name_plural = _("Container Locations")

    def clean(self):
        super().clean()
        if self.yard:
            if (
                self.row is None
                or self.column_start is None
                or self.column_end is None
                or self.tier is None
            ):
                raise ValidationError(
                    _("Row, column, and tier must be specified for yard locations.")
                )

            if self.row > self.yard.max_rows:
                raise ValidationError(_("Row exceeds yard's maximum rows."))

            if (
                self.column_start > self.yard.max_columns
                or self.column_end > self.yard.max_columns
            ):
                raise ValidationError(_("Column exceeds yard's maximum columns."))

            if self.tier > self.yard.max_tiers:
                raise ValidationError(_("Tier exceeds yard's maximum tiers."))

            if self.column_start > self.column_end:
                raise ValidationError(
                    _("Column start cannot be greater than column end.")
                )

    def __str__(self):
        if self.yard:
            return f"{self.container.name} - Yard: {self.yard.name}, Row: {self.row}, Column: {self.column_start}-{self.column_end}, Tier: {self.tier}"
        return f"{self.container.name} - Not in yard"
