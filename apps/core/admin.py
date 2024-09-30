from django.contrib import admin

from apps.core.models import TerminalService, TerminalServiceType, FreeDayCombination

admin.site.register(TerminalService)
admin.site.register(TerminalServiceType)


@admin.register(FreeDayCombination)
class FreeDayCombinationAdmin(admin.ModelAdmin):
    list_display = (
        "container_size",
        "container_state",
        "category",
        "default_free_days",
    )
    search_fields = (
        "container_size",
        "container_state",
        "category",
        "default_free_days",
    )
