from django.contrib import admin

from .models import Branch, BranchAccess


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "status", "phone"]
    list_filter = ["status", "organization"]
    search_fields = ["name", "uuid", "phone"]
    readonly_fields = ["uuid", "created_at", "updated_at"]


@admin.register(BranchAccess)
class BranchAccessAdmin(admin.ModelAdmin):
    list_display = ["branch", "user", "member", "granted_by", "granted_at"]
    list_filter = ["branch"]
    readonly_fields = ["granted_at"]
