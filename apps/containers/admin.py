from django.contrib import admin

from .models import Container, ContainerStorage, ContainerDocument, ContainerImage

admin.site.register(Container)
admin.site.register(ContainerStorage)


@admin.register(ContainerDocument)
class ContainerDocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(ContainerImage)
class ContainerImageAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
