from django.contrib import admin

from .models import FreezeRequest, Membership, MembershipFreeze, MembershipPlan


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "duration_days", "price", "billing_frequency", "status"]
    list_filter = ["status", "billing_frequency", "organization"]
    search_fields = ["name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]


class MembershipFreezeInline(admin.TabularInline):
    model = MembershipFreeze
    extra = 0
    readonly_fields = ["created_at", "revised_end_date"]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["member", "plan", "status", "start_date", "end_date", "price"]
    list_filter = ["status", "organization", "plan"]
    search_fields = ["member__full_name", "member__phone", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["member", "plan", "created_by"]
    inlines = [MembershipFreezeInline]


@admin.register(FreezeRequest)
class FreezeRequestAdmin(admin.ModelAdmin):
    list_display = ["membership", "member", "status", "start_date", "end_date", "requested_by"]
    list_filter = ["status", "organization"]
    search_fields = ["reason", "uuid", "member__full_name"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["membership", "member", "requested_by", "reviewed_by"]
