from django.contrib import admin

from .models import Organization, OrganizationSettings


class OrganizationSettingsInline(admin.StackedInline):
    model = OrganizationSettings
    can_delete = False


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "gstin", "freeze_policy", "created_at"]
    list_filter = ["status", "freeze_policy"]
    search_fields = ["name", "legal_name", "gstin", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    inlines = [OrganizationSettingsInline]
