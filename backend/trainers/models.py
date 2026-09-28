"""Trainer profile extension (REQ-046/047). Staff accounts live in accounts.User;
this model holds trainer-only extras and compensation config. No payroll rows.
"""

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class TrainerProfile(TenantScopedModel):
    class CompensationModel(models.TextChoices):
        FIXED_SALARY = "FIXED_SALARY", "Fixed salary"
        PER_SESSION = "PER_SESSION", "Per session"
        PER_CLASS = "PER_CLASS", "Per class"
        REVENUE_SHARE = "REVENUE_SHARE", "Revenue share"

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="trainer_profile",
    )
    specializations = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    compensation_model = models.CharField(
        max_length=20,
        choices=CompensationModel.choices,
        default=CompensationModel.FIXED_SALARY,
    )
    compensation_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bio = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["organization"], name="trainers_tr_organiz_idx")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"TrainerProfile({self.user_id})"

    def clean(self):
        super().clean()
        if not self.user_id:
            return
        if self.user.role != "TRAINER":
            raise ValidationError("TrainerProfile.user must have role=TRAINER.")
        if self.user.organization_id != self.organization_id:
            raise ValidationError("TrainerProfile.organization must match user.organization.")
