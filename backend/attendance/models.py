"""Attendance / check-in models. See PROJECT_CONTEXT.md §27.A, §20,
REQ-003/004/026..030.
"""

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class Attendance(TenantScopedModel):
    class Method(models.TextChoices):
        STAFF_SEARCH = "STAFF_SEARCH", "Staff search"
        QR = "QR", "QR code"
        BIOMETRIC = "BIOMETRIC", "Biometric/RFID"
        MANUAL_OVERRIDE = "MANUAL_OVERRIDE", "Manual override"

    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="attendances")
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT, related_name="attendances")
    checkin_at = models.DateTimeField()
    checkout_at = models.DateTimeField(null=True, blank=True)
    method = models.CharField(max_length=20, choices=Method.choices)
    device_id = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="attendances_recorded"
    )
    override_reason = models.CharField(
        max_length=255, blank=True, help_text="Required when method=MANUAL_OVERRIDE (AGENTS.md §20.3 auditability)."
    )

    class Meta:
        indexes = [
            models.Index(fields=["member", "checkin_at"]),
            models.Index(fields=["branch", "checkin_at"]),
        ]
        ordering = ["-checkin_at"]

    def __str__(self):
        return f"{self.member} @ {self.branch} ({self.checkin_at})"

    def clean(self):
        super().clean()
        if self.method == self.Method.MANUAL_OVERRIDE:
            if not self.override_reason:
                raise ValidationError("override_reason is required when method=MANUAL_OVERRIDE.")
            if not self.recorded_by_id:
                raise ValidationError("recorded_by is required when method=MANUAL_OVERRIDE.")
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("Attendance.organization must match member.organization.")


class QRToken(TenantScopedModel):
    """One active token per member for V1 (rotation history is a later
    enhancement — not a schema blocker, per §27.A note).

    Deliberately reuses the base `TenantScopedModel.uuid` field (DEC-012)
    as the scannable QR payload itself, rather than adding a second opaque
    identifier — `uuid` already IS "an opaque external identifier safe to
    put in a QR code", so a separate `token` field would just duplicate it.
    """

    member = models.OneToOneField("members.Member", on_delete=models.CASCADE, related_name="qr_token")
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"QRToken({self.member_id})"
