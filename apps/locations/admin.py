from django.contrib import admin

from apps.locations.models import Yard, ContainerLocation

admin.site.register(ContainerLocation)


@admin.register(Yard)
class YardAdmin(admin.ModelAdmin):
    list_display = ("name", "max_rows", "max_columns", "max_tiers")
