"""Member profile model. See PROJECT_CONTEXT.md §27.A, REQ-021..REQ-026.

`Member.status` is DERIVED from the current `Membership` state (REQ-023) —
this app does not own membership lifecycle logic itself (that is the
`memberships` app, added in the same Phase 1 task). Deriving status here
would create the circular-source-of-truth problem `AGENTS.md` §19.2
explicitly forbids ("Do not duplicate membership status logic
independently"), so for now `status` is a plain field defaulted to ACTIVE
at creation and will be recomputed by a `memberships`-owned service once
that app's models exist later in this same task.
"""

from django.core.exceptions import ValidationError
from django.db import models

from core.models import SoftDeleteModel, TenantScopedModel, TenantScopedSoftDeleteManager


class Member(TenantScopedModel, SoftDeleteModel):
    # Explicit combined manager — see TenantScopedSoftDeleteManager
    # docstring in core.models for why this cannot be inherited implicitly.
    objects = TenantScopedSoftDeleteManager()
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"
        UNSPECIFIED = "UNSPECIFIED", "Prefer not to say"

    class ConsentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        GRANTED = "GRANTED", "Granted"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    class Status(models.TextChoices):
        """Derived display status — see module docstring. Authoritative
        recomputation lands with the `memberships` app in this same task."""

        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        EXPIRED = "EXPIRED", "Expired"
        FROZEN = "FROZEN", "Frozen"

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="member_profile",
        help_text="Set once the member is invited to the self-service portal. "
        "A Member can exist before portal access is provisioned.",
    )
    member_code = models.CharField(max_length=32, help_text="Human-friendly ID, e.g. GYM-000123.")
    home_branch = models.ForeignKey(
        "branches.Branch", on_delete=models.PROTECT, related_name="home_members"
    )
    assigned_trainer = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_members",
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.UNSPECIFIED)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="member_photos/", null=True, blank=True)
    medical_notes = models.TextField(
        blank=True, help_text="Sensitive personal data — access must be audited/restricted per AGENTS.md §37."
    )
    consent_status = models.CharField(
        max_length=20, choices=ConsentStatus.choices, default=ConsentStatus.PENDING
    )
    joining_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "phone"], name="unique_member_phone_per_org"),
            models.UniqueConstraint(fields=["organization", "member_code"], name="unique_member_code_per_org"),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
        ]
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.member_code})"

    def clean(self):
        super().clean()
        if self.assigned_trainer_id and self.assigned_trainer.role != "TRAINER":
            raise ValidationError("assigned_trainer must be a user with role=TRAINER.")
        if self.home_branch_id and self.home_branch.organization_id != self.organization_id:
            raise ValidationError("home_branch must belong to the same organization as the member.")
