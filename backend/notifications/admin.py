from django.contrib import admin

from .models import NotificationLog, NotificationTemplate


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["event_type", "channel", "is_active", "organization"]
    list_filter = ["event_type", "channel", "is_active", "organization"]
    search_fields = ["event_type", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ["event_type", "channel", "status", "sent_at", "organization"]
    list_filter = ["status", "channel", "event_type", "organization"]
    search_fields = ["provider_message_id", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at", "sent_at", "provider_message_id"]
    autocomplete_fields = ["recipient_member", "recipient_user"]
