from django.contrib import admin

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["member_code", "full_name", "phone", "organization", "home_branch", "status", "joining_date"]
    list_filter = ["status", "organization", "home_branch", "consent_status"]
    search_fields = ["full_name", "phone", "email", "member_code", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["home_branch", "assigned_trainer", "user"]
