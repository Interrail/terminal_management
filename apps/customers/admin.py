from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Company, CompanyUser


class CompanyUserInline(admin.TabularInline):
    model = CompanyUser
    extra = 1
    autocomplete_fields = ["user"]
    fk_name = "company"


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "slug", "user_count")
    search_fields = ("name", "address", "slug")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CompanyUserInline]

    def user_count(self, obj):
        return obj.company_users.count()

    user_count.short_description = "Number of Users"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("company_users")


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ("company_link", "user_link")
    list_filter = ("company",)
    search_fields = (
        "company__name",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    autocomplete_fields = ["company", "user"]

    def company_link(self, obj):
        url = reverse("admin:customers_company_change", args=[obj.company.id])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)

    company_link.short_description = "Company"
    company_link.admin_order_field = "company__name"

    def user_link(self, obj):
        url = reverse("admin:users_customuser_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)

    user_link.short_description = "User"
    user_link.admin_order_field = "user__email"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("company", "user")
