"""Workout models. See PROJECT_CONTEXT.md §27.A, REQ-056.

No AI coaching / generated plans — assigned programs and member logs only.
"""

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class Exercise(TenantScopedModel):
    """Organization-scoped exercise library (V1: no global catalog)."""

    name = models.CharField(max_length=255)
    muscle_group = models.CharField(max_length=100, blank=True)
    equipment = models.CharField(max_length=100, blank=True)
    instructions = models.TextField(blank=True)
    media_url = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class WorkoutProgram(TenantScopedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"

    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="workout_programs"
    )
    trainer = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="workout_programs_as_trainer"
    )
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        indexes = [models.Index(fields=["organization", "member"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.member_id})"

    def clean(self):
        super().clean()
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("WorkoutProgram.organization must match member.organization.")
        if self.trainer_id and self.trainer.role != "TRAINER":
            raise ValidationError("WorkoutProgram.trainer must have role=TRAINER.")
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("end_date cannot be before start_date.")


class WorkoutDay(TenantScopedModel):
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name="days")
    day_index = models.PositiveIntegerField()
    label = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["program", "day_index"], name="workouts_day_unique_index"),
        ]
        ordering = ["day_index"]

    def __str__(self):
        return f"{self.program_id} day {self.day_index}"

    def clean(self):
        super().clean()
        if self.program_id and self.organization_id and self.program.organization_id != self.organization_id:
            raise ValidationError("WorkoutDay.organization must match program.organization.")


class WorkoutDayExercise(TenantScopedModel):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name="day_prescriptions")
    target_sets = models.PositiveIntegerField()
    target_reps = models.PositiveIntegerField()
    target_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    rest_seconds = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.workout_day_id} -> {self.exercise_id}"

    def clean(self):
        super().clean()
        if (
            self.workout_day_id
            and self.organization_id
            and self.workout_day.organization_id != self.organization_id
        ):
            raise ValidationError("WorkoutDayExercise.organization must match workout_day.organization.")
        if self.exercise_id and self.organization_id and self.exercise.organization_id != self.organization_id:
            raise ValidationError("WorkoutDayExercise.exercise must belong to the same organization.")


class WorkoutLog(TenantScopedModel):
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="workout_logs")
    workout_day_exercise = models.ForeignKey(
        WorkoutDayExercise,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name="logs")
    performed_on = models.DateField()
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "member"])]
        ordering = ["-performed_on", "-created_at"]

    def __str__(self):
        return f"WorkoutLog({self.member_id}, {self.performed_on})"

    def clean(self):
        super().clean()
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("WorkoutLog.organization must match member.organization.")
        if self.exercise_id and self.organization_id and self.exercise.organization_id != self.organization_id:
            raise ValidationError("WorkoutLog.exercise must belong to the same organization.")
        if self.workout_day_exercise_id:
            prescription = self.workout_day_exercise
            program_member_id = prescription.workout_day.program.member_id
            if self.member_id and program_member_id != self.member_id:
                raise ValidationError("WorkoutLog.member must match the prescribed program member.")
            if self.exercise_id and prescription.exercise_id != self.exercise_id:
                raise ValidationError("WorkoutLog.exercise must match the prescribed exercise.")
