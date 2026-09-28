from django.contrib import admin

from audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Append-only: view existing events, never add/change/delete."""

    list_display = [
        "occurred_at",
        "action",
        "resource_type",
        "resource_uuid",
        "actor",
        "organization",
        "system_initiated",
    ]
    list_filter = ["action", "resource_type", "system_initiated", "organization"]
    search_fields = ["action", "resource_type", "request_id", "uuid"]
    ordering = ["-occurred_at"]
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
