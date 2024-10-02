from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ContainerSize(TextChoices):
    TWENTY = "20", _("20 ft Standard")
    TWENTY_HIGH_CUBE = "20HC", _("20 ft High Cube")
    FORTY = "40", _("40 ft Standard")
    FORTY_HIGH_CUBE = "40HC", _("40 ft High Cube")
    FORTY_FIVE = "45", _("45 ft High Cube")


class TransportType(TextChoices):
    AUTO = "auto", _("auto")
    WAGON = "wagon", _("wagon")


class ContainerState(TextChoices):
    LOADED = "loaded", _("loaded")
    EMPTY = "empty", _("empty")
    ANY = "any", _("any")


class MeasurementUnit(TextChoices):
    CONTAINER = "container", _("container")
    DAY = "day", _("day")
    OPERATION = "operation", _("operation")
    UNIT = ("unit",)
