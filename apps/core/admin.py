from django.contrib import admin

from apps.core.models import TerminalService, TerminalServiceType

admin.site.register(TerminalService)
admin.site.register(TerminalServiceType)
