"""Shared DRF permission classes and viewset mixin implementing DEC-008
(multi-tenancy), DEC-009 (branch access), and DEC-011 (authorization).

Every viewset for a tenant-owned resource MUST use
`TenantScopedViewSetMixin` (or reimplement its `get_queryset` contract) so
that the organization scope always comes from the authenticated user, never
from a client-supplied query param / URL segment / request body field
(AGENTS.md §16.2 — non-negotiable).
"""

from rest_framework.permissions import BasePermission


class IsOrgMember(BasePermission):
    """Baseline check: the request has an authenticated user attached to an
    organization. Nearly every endpoint should include this (it is also
    covered implicitly by JWTAuthentication + IsAuthenticated, but this
    makes the organization-scoping intent explicit and defends against a
    future auth backend that authenticates without an organization)."""

    message = "You must belong to an organization to access this resource."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "organization_id", None))


class HasRole(BasePermission):
    """Factory-style permission: `HasRole("OWNER", "STAFF_ADMIN")`.

    Usage: `permission_classes = [HasRole("OWNER", "STAFF_ADMIN")]`
    """

    def __init__(self, *roles):
        self.roles = set(roles)

    def __call__(self):
        # DRF instantiates permission_classes entries with no args; this
        # lets `HasRole("OWNER")` itself be dropped straight into
        # permission_classes (it already IS the instance).
        return self

    message = "You do not have the required role for this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in self.roles)


class HasBranchAccess(BasePermission):
    """Object-level check implementing DEC-009: OWNER bypasses entirely;
    everyone else must match the object's `home_branch` or hold an
    explicit `BranchAccess` grant for it.

    Expects the view to expose `get_branch_for_object(obj)` returning the
    relevant `branches.Branch` instance (objects reach a branch via
    different relations — e.g. `Member.home_branch`, `GymClass.branch` —
    so this cannot be hard-coded to one attribute name).
    """

    message = "You do not have access to this branch."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "OWNER":
            return True

        branch = view.get_branch_for_object(obj) if hasattr(view, "get_branch_for_object") else None
        if branch is None:
            return False

        if getattr(user, "home_branch_id", None) == branch.id:
            return True

        from branches.models import BranchAccess

        return BranchAccess.objects.filter(user=user, branch=branch).exists()


class TenantScopedViewSetMixin:
    """Mandatory mixin for every tenant-owned resource ViewSet.

    Forces `get_queryset()` to always start from `for_user(self.request.user)`
    — the organization filter is structurally derived from the
    authenticated user, and there is no code path here that reads an
    organization id from the request. Subclasses set `queryset` to an
    unfiltered `Model.objects.all()`-style base as usual; this mixin does
    the narrowing.
    """

    def get_queryset(self):
        base_manager = self.queryset.model._default_manager if self.queryset is not None else None
        if base_manager is None:
            raise NotImplementedError(
                "TenantScopedViewSetMixin requires `queryset` to be set on the "
                "viewset (e.g. `queryset = Member.objects.all()`)."
            )
        return base_manager.for_user(self.request.user)
