"""Append-only audit event log (DEC-019, AGENTS.md §38).

Rows are created through `audit.services.audit_log` and must never be
updated or deleted. Django admin is read-only; the queryset and model
refuse `update()` / `delete()` / subsequent `save()` so append-only is
enforced in application code, not only by convention.
"""

from django.db import models

from core.models import TenantScopedModel, TenantScopedQuerySet


class AuditLogImmutableError(Exception):
    """Raised when code attempts to mutate or remove an audit row."""


class AuditLogQuerySet(TenantScopedQuerySet):
    def update(self, **kwargs):
        raise AuditLogImmutableError("AuditLog is append-only; updates are not permitted.")

    def delete(self):
        raise AuditLogImmutableError("AuditLog is append-only; deletes are not permitted.")


class AuditLog(TenantScopedModel):
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100)
    resource_uuid = models.UUIDField(null=True, blank=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    before_state = models.JSONField(null=True, blank=True)
    after_state = models.JSONField(null=True, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)
    request_id = models.CharField(max_length=64, blank=True, default="")
    system_initiated = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(AuditLogQuerySet)()

    class Meta:
        indexes = [
            models.Index(fields=["organization", "occurred_at"]),
            models.Index(fields=["resource_type", "resource_uuid"]),
        ]
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.action} {self.resource_type} @ {self.occurred_at}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise AuditLogImmutableError("AuditLog is append-only; updates are not permitted.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AuditLogImmutableError("AuditLog is append-only; deletes are not permitted.")
