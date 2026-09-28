"""Personal-training models. See PROJECT_CONTEXT.md §27.A, §24, REQ-042..045.

`linked_workout_log` is deferred — the `workouts` app does not exist yet
(same phased-FK pattern as billing.related_pt_package before this task).
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class PTPackage(TenantScopedModel):
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="pt_packages")
    trainer = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="pt_packages")
    plan_name = models.CharField(max_length=255)
    sessions_purchased = models.PositiveIntegerField()
    sessions_consumed = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(sessions_consumed__lte=models.F("sessions_purchased")),
                name="pt_consumed_lte_purchased",
            ),
        ]
        indexes = [models.Index(fields=["organization", "member"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.plan_name} ({self.member_id})"

    @property
    def sessions_remaining(self):
        return self.sessions_purchased - self.sessions_consumed

    def clean(self):
        super().clean()
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("PTPackage.organization must match member.organization.")
        if self.trainer_id and self.trainer.role != "TRAINER":
            raise ValidationError("PTPackage.trainer must have role=TRAINER.")
        if self.sessions_consumed > self.sessions_purchased:
            raise ValidationError("sessions_consumed cannot exceed sessions_purchased.")


class PTSession(TenantScopedModel):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No-show"
        RESCHEDULED = "RESCHEDULED", "Rescheduled"

    package = models.ForeignKey(PTPackage, on_delete=models.PROTECT, related_name="sessions")
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="pt_sessions")
    trainer = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="pt_sessions")
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["trainer", "scheduled_at"]), models.Index(fields=["member", "scheduled_at"])]
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"PTSession({self.member_id}, {self.scheduled_at}, {self.status})"

    def clean(self):
        super().clean()
        if self.package_id and self.member_id and self.package.member_id != self.member_id:
            raise ValidationError("PTSession.member must match package.member.")
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("PTSession.organization must match member.organization.")
