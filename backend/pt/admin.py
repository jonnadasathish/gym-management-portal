from django.contrib import admin

from .models import PTPackage, PTSession


@admin.register(PTPackage)
class PTPackageAdmin(admin.ModelAdmin):
    list_display = ["plan_name", "member", "trainer", "sessions_purchased", "sessions_consumed", "expiry_date"]
    list_filter = ["organization"]
    search_fields = ["plan_name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["member", "trainer"]


@admin.register(PTSession)
class PTSessionAdmin(admin.ModelAdmin):
    list_display = ["member", "trainer", "scheduled_at", "status"]
    list_filter = ["status", "organization"]
    search_fields = ["member__full_name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["package", "member", "trainer"]
