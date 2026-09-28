from django.contrib import admin

from .models import Attendance, QRToken


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["member", "branch", "checkin_at", "checkout_at", "method", "recorded_by"]
    list_filter = ["method", "branch", "organization"]
    search_fields = ["member__full_name", "member__phone", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["member", "branch", "recorded_by"]


@admin.register(QRToken)
class QRTokenAdmin(admin.ModelAdmin):
    list_display = ["member", "uuid", "issued_at", "expires_at"]
    readonly_fields = ["uuid", "issued_at", "created_at", "updated_at"]
    autocomplete_fields = ["member"]
