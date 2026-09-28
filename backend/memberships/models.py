"""Membership lifecycle models. See PROJECT_CONTEXT.md §27.A, §19,
REQ-005/007/020/023/024/025.

`Membership` is a full `TenantScopedModel` (denormalized `organization`,
kept in sync with `member.organization` via `clean()`) rather than being
scoped only transitively through `member` — this keeps every tenant-owned
model in the codebase using the same `for_organization()`/`for_user()`
convention uniformly, per the pattern established in `core.models`.

`MembershipFreeze` is NOT independently tenant-scoped — it is always
accessed through its `membership` relation, matching the original §27.A
sketch (no `organization` field listed there for it).
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class MembershipPlan(TenantScopedModel):
    class BillingFrequency(models.TextChoices):
        ONE_TIME = "ONE_TIME", "One-time"
        MONTHLY = "MONTHLY", "Monthly"
        QUARTERLY = "QUARTERLY", "Quarterly"
        HALF_YEARLY = "HALF_YEARLY", "Half-yearly"
        ANNUAL = "ANNUAL", "Annual"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"

    name = models.CharField(max_length=255)
    duration_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_frequency = models.CharField(max_length=20, choices=BillingFrequency.choices)
    freeze_allowed = models.BooleanField(default=True)
    max_freeze_days = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        indexes = [models.Index(fields=["organization", "status"])]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.organization_id})"


class Membership(TenantScopedModel):
    class Status(models.TextChoices):
        """Exactly the states named in AGENTS.md §19.2 — no unsupported
        states added without documented reason."""

        ACTIVE = "ACTIVE", "Active"
        FROZEN = "FROZEN", "Frozen"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="memberships")
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name="memberships")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Snapshot at sale — plan price changes never retroactively alter this."
    )
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="memberships_created"
    )

    class Meta:
        indexes = [
            models.Index(fields=["member", "status"]),
            models.Index(fields=["end_date"]),
        ]
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.member} — {self.plan} ({self.status})"

    def clean(self):
        super().clean()
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("Membership.organization must match member.organization.")
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("end_date cannot be before start_date.")


class MembershipFreeze(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name="freezes")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    requested_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="freezes_requested"
    )
    approved_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="freezes_approved"
    )
    revised_end_date = models.DateField(
        help_text="The membership.end_date computed and stored at the moment this freeze was applied, for audit."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Freeze({self.membership_id}, {self.start_date}..{self.end_date})"


class FreezeRequest(TenantScopedModel):
    """Member-submitted freeze request. Staff approve/reject only — never
    auto-approved (REQ-020). Dates must be supplied by the requester;
    this model does not invent defaults."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    membership = models.ForeignKey(
        Membership, on_delete=models.PROTECT, related_name="freeze_requests"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="freeze_requests"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="freeze_requests_requested",
    )
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="freeze_requests_reviewed",
    )

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["member", "status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"FreezeRequest({self.membership_id}, {self.status})"

    def clean(self):
        super().clean()
        if self.membership_id and self.organization_id:
            if self.membership.organization_id != self.organization_id:
                raise ValidationError("FreezeRequest.organization must match membership.organization.")
        if self.membership_id and self.member_id:
            if self.membership.member_id != self.member_id:
                raise ValidationError("FreezeRequest.member must match membership.member.")
