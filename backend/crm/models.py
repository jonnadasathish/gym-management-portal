"""Lead CRM models (PRD Should — REQ-048). Pipeline only; no marketing automation."""

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class Lead(TenantScopedModel):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        CONTACTED = "CONTACTED", "Contacted"
        TRIAL_SCHEDULED = "TRIAL_SCHEDULED", "Trial scheduled"
        TRIAL_ATTENDED = "TRIAL_ATTENDED", "Trial attended"
        PROPOSAL = "PROPOSAL", "Proposal"
        CONVERTED = "CONVERTED", "Converted"
        LOST = "LOST", "Lost"

    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT, related_name="leads")
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    source = models.CharField(max_length=100, blank=True)
    interested_plan = models.ForeignKey(
        "memberships.MembershipPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    assigned_staff = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
    )
    trial_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    next_follow_up = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    converted_member = models.ForeignKey(
        "members.Member",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="converted_from_leads",
    )

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "branch"]),
            models.Index(fields=["assigned_staff"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"

    def clean(self):
        super().clean()
        if self.branch_id and self.organization_id and self.branch.organization_id != self.organization_id:
            raise ValidationError("Lead.branch must belong to the same organization.")
        if (
            self.interested_plan_id
            and self.organization_id
            and self.interested_plan.organization_id != self.organization_id
        ):
            raise ValidationError("Lead.interested_plan must belong to the same organization.")
        if (
            self.assigned_staff_id
            and self.organization_id
            and self.assigned_staff.organization_id != self.organization_id
        ):
            raise ValidationError("Lead.assigned_staff must belong to the same organization.")
        if (
            self.converted_member_id
            and self.organization_id
            and self.converted_member.organization_id != self.organization_id
        ):
            raise ValidationError("Lead.converted_member must belong to the same organization.")


class LeadActivity(TenantScopedModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_activities_created",
    )

    class Meta:
        indexes = [models.Index(fields=["lead", "created_at"])]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.activity_type} ({self.lead_id})"

    def clean(self):
        super().clean()
        if self.lead_id and self.organization_id and self.lead.organization_id != self.organization_id:
            raise ValidationError("LeadActivity.organization must match lead.organization.")
