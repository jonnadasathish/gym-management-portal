"""Shared abstract base models used by every tenant-owned app.

See PROJECT_CONTEXT.md §27.A and DEC-008/DEC-012 for the design rationale.
No app should hand-roll its own `organization` FK / `uuid` / timestamp
fields — inherit from these instead, so tenant scoping and external
identifiers stay consistent everywhere.
"""

import uuid as uuid_lib

from django.db import models


class TimestampedModel(models.Model):
    """Adds created_at / updated_at to any model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantScopedQuerySet(models.QuerySet):
    def for_organization(self, organization):
        """The canonical, explicit way to scope a queryset to one tenant.

        Every view/service MUST reach the database through this method (or
        the equivalent `TenantScopedManager.for_user`) — never through a
        bare `Model.objects.all()` — per AGENTS.md §16.2 (never trust a
        client-supplied organization_id; the authenticated user's
        organization is the only valid scope).
        """
        return self.filter(organization=organization)

    def for_user(self, user):
        """Scope to the organization of the *authenticated* user. This is
        the primary call sites (views/services) should use — it makes it
        structurally impossible to accidentally scope by a client-supplied
        value, because it only ever reads `user.organization`.
        """
        return self.for_organization(user.organization)


class TenantScopedManager(models.Manager.from_queryset(TenantScopedQuerySet)):
    """Default manager for TenantScopedModel.

    NOTE on DEC-008 implementation: the decision log describes the model
    layer as refusing to return an unscoped queryset. In practice, fully
    disabling `.objects.all()` would also break Django internals that
    reasonably need unscoped access (admin site, `createsuperuser`,
    migrations, management commands, audit/reporting jobs that
    intentionally span organizations). Instead, enforcement is layered as
    designed, with the *model* layer providing unmistakable, hard-to-misuse
    helpers (`for_user`, `for_organization`) as the paved path, and the
    *view* layer (`core.permissions`/`TenantScopedViewSetMixin`, added when
    the first API views are built) as the actual hard boundary that DRF
    endpoints cannot bypass. This refinement is recorded here rather than
    silently deviating from the decision log — see PROJECT_CONTEXT.md
    GYM-005 for the explicit note.
    """

    pass


class TenantScopedModel(TimestampedModel):
    """Base class for every tenant-owned model in the system.

    `organization` uses a lazy ("organizations.Organization") string
    reference to avoid a circular import between `core` and
    `organizations` (core must not import organizations.models directly).
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="+",
        db_index=True,
    )
    uuid = models.UUIDField(
        default=uuid_lib.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="Opaque external identifier. Use this in API URLs / QR "
        "codes — never expose the internal integer primary key (DEC-012).",
    )

    objects = TenantScopedManager()

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class TenantScopedSoftDeleteQuerySet(TenantScopedQuerySet, SoftDeleteQuerySet):
    """Combined queryset for models that are BOTH tenant-scoped AND
    soft-deletable (e.g. Member). Plain multiple inheritance of two
    `QuerySet` mixins works fine here since both only add simple `filter()`
    methods with no overlapping method names.

    NOTE: when a model inherits both `TenantScopedModel` and
    `SoftDeleteModel`, Django only keeps ONE `_default_manager` (the first
    one found in MRO order) — the other mixin's manager is silently
    shadowed. Any such model MUST explicitly set
    `objects = TenantScopedSoftDeleteManager()` itself rather than relying
    on either parent's manager. This was caught by a failing test
    (`members/tests/test_models.py::test_member_soft_delete`) rather than
    designed up front — see PROJECT_CONTEXT.md GYM-006 for the correction
    record.
    """

    pass


class TenantScopedSoftDeleteManager(models.Manager.from_queryset(TenantScopedSoftDeleteQuerySet)):
    pass


class SoftDeleteModel(models.Model):
    """Opt-in mixin for models where "soft delete" is the correct business
    behavior (e.g. Member). Never use this for financial rows — those use
    explicit state transitions instead (AGENTS.md §21.7/§34.4, DEC-018).
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])
