from django.contrib import admin

from .models import Lead, LeadActivity


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "status", "branch", "assigned_staff", "organization"]
    list_filter = ["status", "organization"]
    search_fields = ["name", "phone", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["branch", "interested_plan", "assigned_staff", "converted_member"]


@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ["lead", "activity_type", "created_by", "created_at"]
    list_filter = ["organization"]
    search_fields = ["activity_type", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["lead", "created_by"]
