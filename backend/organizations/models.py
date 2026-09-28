"""Organization (tenant) models. See PROJECT_CONTEXT.md §27.A and DEC-008.

`Organization` is the tenant root — it does NOT inherit `TenantScopedModel`
(it IS the tenant, not a tenant-owned resource).
"""

import uuid as uuid_lib

from django.db import models

from core.models import TimestampedModel


class Organization(TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"

    class FreezePolicy(models.TextChoices):
        """The schema stores the *choice*; which policy is the correct
        default is OQ-005 (PROJECT_CONTEXT.md §38) and remains open."""

        EXTEND_BY_FREEZE_DAYS = "EXTEND_BY_FREEZE_DAYS", "Extend end date by frozen days"
        PAUSE_NO_EXTEND = "PAUSE_NO_EXTEND", "Pause membership, no automatic extension"

    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    gstin = models.CharField(max_length=15, blank=True, help_text="GST identification number, if registered.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    default_timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    default_currency = models.CharField(max_length=3, default="INR")
    freeze_policy = models.CharField(
        max_length=32,
        choices=FreezePolicy.choices,
        default=FreezePolicy.EXTEND_BY_FREEZE_DAYS,
        help_text="Default policy is a placeholder pending OQ-005 confirmation.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationSettings(models.Model):
    """1:1 split from Organization to avoid a bloated root row (§27.A)."""

    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="settings"
    )
    invoice_number_prefix = models.CharField(max_length=20, default="INV")
    invoice_number_next_sequence = models.PositiveIntegerField(default=1)
    notification_defaults = models.JSONField(default=dict, blank=True)
    billing_defaults = models.JSONField(default=dict, blank=True)
    min_checkin_interval_minutes = models.PositiveIntegerField(
        default=120,
        help_text="Provisional duplicate-check-in window (minutes). Product rule still open.",
    )

    def __str__(self):
        return f"Settings for {self.organization.name}"
