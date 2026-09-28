"""Notification templates and delivery logs.

WhatsApp/SMS/email vendors are not wired (OQ-001/002). Delivery in this
app is in-app / local log only via `ConsoleNotificationProvider`.
"""

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class NotificationEventType(models.TextChoices):
    """PRD §8.9 mandatory transactional events."""

    MEMBERSHIP_CREATED = "MEMBERSHIP_CREATED", "Membership created"
    PAYMENT_SUCCESSFUL = "PAYMENT_SUCCESSFUL", "Payment successful"
    PAYMENT_FAILED = "PAYMENT_FAILED", "Payment failed"
    MEMBERSHIP_EXPIRING = "MEMBERSHIP_EXPIRING", "Membership expiring"
    MEMBERSHIP_EXPIRED = "MEMBERSHIP_EXPIRED", "Membership expired"
    CLASS_BOOKING = "CLASS_BOOKING", "Class booking"
    CLASS_REMINDER = "CLASS_REMINDER", "Class reminder"
    PT_BOOKING = "PT_BOOKING", "PT booking"
    PT_REMINDER = "PT_REMINDER", "PT reminder"
    BIRTHDAY = "BIRTHDAY", "Birthday"
    FREEZE_APPROVED = "FREEZE_APPROVED", "Freeze approved"


class NotificationChannel(models.TextChoices):
    WHATSAPP = "WHATSAPP", "WhatsApp"
    SMS = "SMS", "SMS"
    EMAIL = "EMAIL", "Email"
    IN_APP = "IN_APP", "In-app"


class NotificationTemplate(TenantScopedModel):
    event_type = models.CharField(max_length=32, choices=NotificationEventType.choices)
    channel = models.CharField(max_length=16, choices=NotificationChannel.choices)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "event_type", "channel"],
                name="unique_notification_template_per_org_event_channel",
            ),
        ]
        indexes = [models.Index(fields=["organization", "event_type", "channel"])]
        ordering = ["event_type", "channel"]

    def __str__(self):
        return f"{self.event_type}/{self.channel}"


class NotificationLog(TenantScopedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    recipient_member = models.ForeignKey(
        "members.Member",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_logs",
    )
    recipient_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_logs",
    )
    event_type = models.CharField(max_length=32, choices=NotificationEventType.choices)
    channel = models.CharField(max_length=16, choices=NotificationChannel.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    provider_message_id = models.CharField(max_length=128, blank=True)
    error_detail = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "event_type"]),
            models.Index(fields=["organization", "recipient_member"]),
            models.Index(fields=["organization", "recipient_user"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"NotificationLog({self.event_type}, {self.status})"

    def clean(self):
        super().clean()
        if (
            self.recipient_member_id
            and self.organization_id
            and self.recipient_member.organization_id != self.organization_id
        ):
            raise ValidationError("NotificationLog.organization must match recipient_member.organization.")
        if (
            self.recipient_user_id
            and self.organization_id
            and self.recipient_user.organization_id != self.organization_id
        ):
            raise ValidationError("NotificationLog.organization must match recipient_user.organization.")
