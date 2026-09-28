"""Member progress models. See PROJECT_CONTEXT.md §27.A, REQ workout/progress.

`PersonalBest.exercise_name` is a CharField, not an FK to `workouts.Exercise`
— the `workouts` app may not be installed yet (same phased-FK pattern as
`pt.PTSession.linked_workout_log`). Photos are stored as a URL string only;
do not add ImageField/S3 in V1 of this app.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class ProgressEntry(TenantScopedModel):
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="progress_entries")
    recorded_at = models.DateTimeField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    body_fat_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    measurements = models.JSONField(default=dict, blank=True)
    photo_url = models.CharField(max_length=512, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "member", "recorded_at"])]
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"ProgressEntry({self.member_id}, {self.recorded_at})"

    @property
    def bmi(self):
        """BMI = weight_kg / (height_m^2) when both weight and height are set.

        height_m is height_cm / 100. Returns None if either value is missing
        or height is not a positive length (avoids division by zero).
        """
        if self.weight_kg is None or self.height_cm is None:
            return None
        height_m = self.height_cm / Decimal("100")
        if height_m <= 0:
            return None
        return self.weight_kg / (height_m * height_m)

    def clean(self):
        super().clean()
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("ProgressEntry.organization must match member.organization.")


class PersonalBest(TenantScopedModel):
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="personal_bests")
    exercise_name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=32)
    achieved_at = models.DateField()

    class Meta:
        ordering = ["-achieved_at"]

    def __str__(self):
        return f"PersonalBest({self.member_id}, {self.exercise_name}, {self.value} {self.unit})"

    def clean(self):
        super().clean()
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("PersonalBest.organization must match member.organization.")
