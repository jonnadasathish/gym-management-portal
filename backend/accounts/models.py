"""Custom User model + auth-support models. See PROJECT_CONTEXT.md §27.A,
DEC-010 (JWT), DEC-011 (authorization), DEC-009 (branch access).

Implementation refinements vs. the original §27.A sketch (recorded here and
in PROJECT_CONTEXT.md GYM-005, not applied silently):

1. `email` is globally unique (not merely per-organization) — see
   accounts.managers.UserManager docstring for why.
2. `organization` is nullable ONLY to allow a platform-level Django
   superuser (`is_superuser=True`, accessed via /admin/ for
   operational/infrastructure purposes) that is not tied to any single
   gym. This is NOT a new business role — AGENTS.md §8.1 permits
   technical/service accounts that are not product roles, and explicitly
   forbids inventing new business roles. Every real business user (the 4
   PRD roles below) MUST have `organization` set; this is enforced in
   `clean()` rather than a DB constraint, to keep the escape hatch usable
   for `createsuperuser` while still catching the mistake for real users.
"""

import uuid as uuid_lib

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimestampedModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        STAFF_ADMIN = "STAFF_ADMIN", "Staff / Front Desk Admin"
        TRAINER = "TRAINER", "Trainer / Coach"
        MEMBER = "MEMBER", "Member"

    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, unique=True, db_index=True)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
        help_text="Required for every business user. Null is reserved for "
        "platform-level Django superusers only (not a product role).",
    )
    home_branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="staff_members",
        null=True,
        blank=True,
        help_text="Required for STAFF_ADMIN/TRAINER/MEMBER. Null for OWNER "
        "(owners implicitly have all branches in their organization).",
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False, help_text="Controls Django /admin/ access — unrelated to the STAFF_ADMIN product role."
    )
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        indexes = [
            models.Index(fields=["organization", "role"]),
        ]

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        if not self.is_superuser and not self.organization_id:
            raise ValidationError("organization is required for every non-superuser account.")
        if self.role == self.Role.OWNER and self.home_branch_id:
            raise ValidationError("OWNER accounts must not have a home_branch (they access all branches).")
        if self.role and self.role != self.Role.OWNER and not self.home_branch_id and not self.is_superuser:
            raise ValidationError("home_branch is required for STAFF_ADMIN, TRAINER, and MEMBER accounts.")


class PasswordResetToken(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token_hash = models.CharField(max_length=128, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Password reset token for {self.user_id}"
