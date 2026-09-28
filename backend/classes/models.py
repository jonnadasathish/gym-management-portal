"""Class scheduling models. See PROJECT_CONTEXT.md §27.A, §23, REQ-008/016.

`Waitlist` is represented as `Booking.status=WAITLISTED` rather than a
second table — one source of truth for “this member holds a relationship
to this occurrence”. Automatic waitlist promotion is NOT implemented
(AGENTS.md §23.4 — policy not finalized).
"""

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class GymClass(TenantScopedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"

    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT, related_name="gym_classes")
    name = models.CharField(max_length=255)
    trainer = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="gym_classes", null=True, blank=True
    )
    room = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField()
    recurrence_rule = models.JSONField(default=dict, blank=True)
    booking_policy = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(capacity__gt=0), name="gym_class_capacity_positive"),
        ]
        indexes = [models.Index(fields=["organization", "status"])]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.branch_id and self.organization_id and self.branch.organization_id != self.organization_id:
            raise ValidationError("GymClass.organization must match branch.organization.")
        if self.trainer_id and self.trainer.role != "TRAINER":
            raise ValidationError("GymClass.trainer must have role=TRAINER.")


class ClassOccurrence(TenantScopedModel):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CANCELLED = "CANCELLED", "Cancelled"

    gym_class = models.ForeignKey(GymClass, on_delete=models.PROTECT, related_name="occurrences")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity_override = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)

    class Meta:
        indexes = [
            models.Index(fields=["gym_class", "start_time"]),
            models.Index(fields=["organization", "start_time"]),
        ]
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.gym_class_id} @ {self.start_time}"

    @property
    def effective_capacity(self):
        return self.capacity_override if self.capacity_override is not None else self.gym_class.capacity

    def clean(self):
        super().clean()
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError("end_time must be after start_time.")
        if self.gym_class_id and self.organization_id and self.gym_class.organization_id != self.organization_id:
            raise ValidationError("ClassOccurrence.organization must match gym_class.organization.")


class Booking(TenantScopedModel):
    class Status(models.TextChoices):
        BOOKED = "BOOKED", "Booked"
        WAITLISTED = "WAITLISTED", "Waitlisted"
        CANCELLED = "CANCELLED", "Cancelled"
        ATTENDED = "ATTENDED", "Attended"
        NO_SHOW = "NO_SHOW", "No-show"

    occurrence = models.ForeignKey(ClassOccurrence, on_delete=models.PROTECT, related_name="bookings")
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="class_bookings")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BOOKED)
    booked_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["occurrence", "status"]), models.Index(fields=["member", "status"])]
        ordering = ["-booked_at"]

    def __str__(self):
        return f"Booking({self.member_id}, {self.occurrence_id}, {self.status})"

    def clean(self):
        super().clean()
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("Booking.organization must match member.organization.")
