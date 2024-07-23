from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Container, ContainerTerminalVisit, ContainerDocument, ContainerImage


class ContainerStorageInline(admin.TabularInline):
    model = ContainerTerminalVisit
    fk_name = "container"
    extra = 1
    fields = ("customer", "entry_time", "exit_time", "storage_days", "is_empty")
    readonly_fields = ("storage_days",)
    autocomplete_fields = ["customer"]


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "storage_status",
        "current_customer",
        "storage_count",
        "is_deleted",
    )
    list_filter = ("type", "deleted")
    search_fields = ("name",)
    inlines = [ContainerStorageInline]

    def get_queryset(self, request):
        return Container.all_objects.all()

    def storage_status(self, obj):
        return "In Storage" if obj.in_storage else "Not in Storage"

    storage_status.short_description = _("Storage Status")

    def current_customer(self, obj):
        current_storage = obj.terminal_visits.filter(exit_time=None).first()
        if current_storage:
            url = reverse(
                "admin:customers_company_change", args=[current_storage.customer.id]
            )
            return format_html(
                '<a href="{}">{}</a>', url, current_storage.customer.name
            )
        return "-"

    current_customer.short_description = _("Current Customer")

    def storage_count(self, obj):
        return obj.terminal_visits.count()

    storage_count.short_description = _("Total Storages")

    def is_deleted(self, obj):
        return obj.deleted

    is_deleted.boolean = True
    is_deleted.short_description = _("Deleted")

    actions = ["restore_containers", "hard_delete_containers"]

    def restore_containers(self, request, queryset):
        restored = queryset.filter(deleted=True).update(deleted=False, deleted_at=None)
        from gettext import ngettext

        self.message_user(
            request,
            ngettext(
                "%d container was successfully restored.",
                "%d containers were successfully restored.",
                restored,
            )
            % restored,
            messages.SUCCESS,
        )

    def hard_delete_containers(self, request, queryset):
        deleted, _ = queryset.hard_delete()
        from gettext import ngettext

        self.message_user(
            request,
            ngettext(
                "%d container was successfully deleted.",
                "%d containers were successfully deleted.",
                deleted,
            )
            % deleted,
            messages.SUCCESS,
        )

    restore_containers.short_description = _("Restore selected containers")
    hard_delete_containers.short_description = _("Hard delete selected containers")


@admin.register(ContainerTerminalVisit)
class ContainerStorageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "container_link",
        "customer_link",
        "entry_time",
        "exit_time",
        "storage_days",
        "is_empty",
        "status",
        "is_deleted",
    )
    list_filter = ("is_empty", "entry_time", "exit_time")
    search_fields = ("container__name", "customer__name", "notes")
    readonly_fields = ("storage_days",)
    autocomplete_fields = ["container", "customer"]
    fieldsets = (
        (None, {"fields": ("container", "customer", "is_empty")}),
        (_("Timing"), {"fields": ("entry_time", "exit_time", "storage_days")}),
        (_("Additional Information"), {"fields": ("notes",)}),
    )

    def container_link(self, obj):
        url = reverse("admin:containers_container_change", args=[obj.container.id])
        return format_html('<a href="{}">{}</a>', url, obj.container.name)

    container_link.short_description = _("Container")
    container_link.admin_order_field = "container__name"

    def customer_link(self, obj):
        url = reverse("admin:customers_company_change", args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.name)

    customer_link.short_description = _("Customer")
    customer_link.admin_order_field = "customer__name"

    def status(self, obj):
        return _("In Storage") if obj.exit_time is None else _("Exited")

    status.short_description = _("Status")
    actions = ["restore_containers", "hard_delete_containers"]

    def is_deleted(self, obj):
        return obj.deleted

    is_deleted.boolean = True
    is_deleted.short_description = _("Deleted")

    def restore_containers(self, request, queryset):
        restored = queryset.filter(deleted=True).update(deleted=False, deleted_at=None)
        from gettext import ngettext

        self.message_user(
            request,
            ngettext(
                "%d container was successfully restored.",
                "%d containers were successfully restored.",
                restored,
            )
            % restored,
            messages.SUCCESS,
        )

    def hard_delete_containers(self, request, queryset):
        deleted, _ = queryset.hard_delete()

        from gettext import ngettext

        self.message_user(
            request,
            ngettext(
                "%d container was successfully deleted.",
                "%d containers were successfully deleted.",
                deleted,
            )
            % deleted,
            messages.SUCCESS,
        )

    restore_containers.short_description = _("Restore selected containers")
    hard_delete_containers.short_description = _("Hard delete selected containers")

    def get_queryset(self, request):
        return ContainerTerminalVisit.all_objects.prefetch_related(
            "container", "customer"
        )


@admin.register(ContainerDocument)
class ContainerDocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(ContainerImage)
class ContainerImageAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
