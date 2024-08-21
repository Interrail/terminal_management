from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ContainerType(TextChoices):
    TWENTY = "20", _("20 ft Standard")
    FORTY = "40", _("40 ft Standard")
    FORTY_HIGH_CUBE = "40HC", _("40 ft High Cube")
    FORTY_FIVE = "45", _("45 ft High Cube")
