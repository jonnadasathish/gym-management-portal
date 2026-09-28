"""Shared API helpers for tenant-owned viewsets (DEC-008/009/015)."""

from rest_framework.response import Response

from branches.models import BranchAccess


STAFF_ROLES = ("OWNER", "STAFF_ADMIN")
FRONT_DESK_ROLES = ("OWNER", "STAFF_ADMIN")
STAFF_AND_TRAINER = ("OWNER", "STAFF_ADMIN", "TRAINER")


def authorized_branch_ids(user):
    """Branches a non-OWNER user may operate on (DEC-009)."""
    ids = set()
    if getattr(user, "home_branch_id", None):
        ids.add(user.home_branch_id)
    ids.update(BranchAccess.objects.filter(user=user).values_list("branch_id", flat=True))
    return ids


def user_may_access_branch(user, branch):
    if user.role == "OWNER":
        return branch.organization_id == user.organization_id
    return branch.id in authorized_branch_ids(user)


class EnvelopeMixin:
    """Wrap non-paginated success payloads in `{data: ...}` (DEC-015).

    Paginated list responses already include `data`/`meta` from
    `StandardPageNumberPagination` and must not be wrapped again.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if response.exception or response.status_code >= 400:
            return response
        payload = response.data
        if isinstance(payload, dict) and ("data" in payload or "error" in payload):
            return response
        response.data = {"data": payload}
        return response


class UUIDLookupMixin:
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"


class TenantScopedAPIMixin(EnvelopeMixin, UUIDLookupMixin):
    """Compose the three contracts every tenant-owned viewset must keep."""

    def get_queryset(self):
        from core.permissions import TenantScopedViewSetMixin

        qs = TenantScopedViewSetMixin.get_queryset(self)
        return self.restrict_queryset(qs)

    def restrict_queryset(self, qs):
        return qs
