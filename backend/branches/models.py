"""Branch and branch-access-grant models. See PROJECT_CONTEXT.md §27.A,
DEC-009 (branch access model)."""

from django.db import models
from django.db.models import UniqueConstraint

from core.models import TenantScopedModel


class Branch(TenantScopedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    operating_hours = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        indexes = [models.Index(fields=["organization", "status"])]
        ordering = ["name"]

    def __str__(self):
        return self.name


class BranchAccess(models.Model):
    """Grants a staff/trainer *user* OR a *member* access to a branch that
    is not their home branch (DEC-009). Exactly one of `user` / `member`
    must be set — enforced by a DB CheckConstraint.

    PHASED SCHEMA NOTE: the `member` FK was deferred from Phase 0 (GYM-005)
    to this Phase 1 task because `members` did not exist as an installed
    app yet, and Django's migration framework cannot resolve a lazy
    `ForeignKey("members.Member")` reference to an app that isn't
    registered. Added now that `members` exists (GYM-006).
    """

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True, related_name="branch_access_grants"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, null=True, blank=True, related_name="branch_access_grants"
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="access_grants")
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="branch_access_grants_made"
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=["user", "branch"], name="unique_user_branch_access"),
            UniqueConstraint(fields=["member", "branch"], name="unique_member_branch_access"),
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, member__isnull=True)
                    | models.Q(user__isnull=True, member__isnull=False)
                ),
                name="branch_access_exactly_one_of_user_or_member",
            ),
        ]

    def __str__(self):
        holder = self.user or self.member
        return f"{holder} -> {self.branch}"
