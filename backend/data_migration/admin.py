from django.contrib import admin

from .models import ImportJob, ImportRowError


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ["entity_type", "status", "uploaded_by", "total_rows", "valid_rows", "error_rows", "organization"]
    list_filter = ["status", "entity_type", "organization"]
    search_fields = ["uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["uploaded_by"]


@admin.register(ImportRowError)
class ImportRowErrorAdmin(admin.ModelAdmin):
    list_display = ["job", "row_number"]
    search_fields = ["job__uuid"]
    autocomplete_fields = ["job"]
