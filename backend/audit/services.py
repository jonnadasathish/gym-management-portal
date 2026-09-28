"""Explicit audit-event writer (DEC-019).

Call this from sensitive service-layer operations. Do not update or
delete existing rows — `AuditLog` is append-only.
"""

from audit.models import AuditLog


def audit_log(
    *,
    organization,
    actor=None,
    action,
    resource_type,
    resource_uuid=None,
    branch=None,
    before=None,
    after=None,
    request_id="",
    system_initiated=False,
):
    """Create one `AuditLog` row. Never updates or deletes."""

    return AuditLog.objects.create(
        organization=organization,
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_uuid=resource_uuid,
        branch=branch,
        before_state=before,
        after_state=after,
        request_id=request_id or "",
        system_initiated=system_initiated,
    )
