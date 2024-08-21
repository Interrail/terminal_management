from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.choices import ContainerType


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Container(models.Model):
    name = models.CharField(
        max_length=12, unique=True, db_index=True, verbose_name=_("Container Name")
    )
    type = models.CharField(
        max_length=4, choices=ContainerType.choices, verbose_name=_("Container Type")
    )

    class Meta:
        db_table = "container"
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    @property
    def in_storage(self):
        return self.storages.filter(exit_time__isnull=True).exists()

    @property
    def teu(self):
        size = self.type
        if size == ContainerType.TWENTY:
            return 1
        else:
            return 2
