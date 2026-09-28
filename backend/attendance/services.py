"""Attendance / check-in business logic (AGENTS.md §20).

DUPLICATE-CHECKIN CAVEAT (recorded, not silently assumed): PRD §8.2 says
duplicate check-ins are "prevented according to configurable rules" without
specifying the exact interval. `MIN_CHECKIN_INTERVAL_MINUTES` below is a
provisional default (2 hours) chosen so the eligibility mechanism is
testable end-to-end; it is NOT an approved business policy. Making this
organization-configurable (mirroring the `Organization.freeze_policy`
pattern) is a follow-up task once product confirms the desired interval —
tracked in PROJECT_CONTEXT.md, not hidden.

Performance note: this is on the critical, latency-sensitive check-in path
(AGENTS.md §20.4 — target <2s backend processing). The eligibility checks
below are all simple indexed lookups (member/branch/checkin_at indexes
already exist per attendance.models.Attendance.Meta), not full scans.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from branches.models import BranchAccess
from memberships.models import Membership

from .models import Attendance

MIN_CHECKIN_INTERVAL_MINUTES = 120  # provisional default — see module docstring


class AttendanceEligibilityError(Exception):
    """Raised with a machine-readable `.code` so the API layer can surface
    a clear reason to front-desk staff (AGENTS.md §20 "clear reason")."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def _duplicate_interval_minutes(member):
    from organizations.models import OrganizationSettings

    try:
        return member.organization.settings.min_checkin_interval_minutes
    except OrganizationSettings.DoesNotExist:
        return MIN_CHECKIN_INTERVAL_MINUTES


def _member_has_active_membership(member, at):
    return Membership.objects.filter(
        member=member,
        status=Membership.Status.ACTIVE,
        start_date__lte=at.date(),
        end_date__gte=at.date(),
    ).exists()


def _member_may_use_branch(member, branch):
    if member.home_branch_id == branch.id:
        return True
    return BranchAccess.objects.filter(member=member, branch=branch).exists()


@transaction.atomic
def check_in(*, member, branch, method, device_id="", recorded_by=None, override_reason="", at=None):
    """Record a check-in after validating eligibility. `at` is injectable
    for tests; defaults to now().

    MANUAL_OVERRIDE bypasses the branch-permission and duplicate-checkin
    checks (that is the point of an override — staff are consciously
    admitting someone who fails the automatic rule) but NEVER bypasses the
    "member is not soft-deleted" check, and REQUIRES `recorded_by` +
    `override_reason` (enforced again here, not only in Model.clean(), so
    the error is raised before any other side effect).
    """

    at = at or timezone.now()
    is_override = method == Attendance.Method.MANUAL_OVERRIDE

    if member.is_deleted:
        raise AttendanceEligibilityError("ACCOUNT_BLOCKED", "This member's account is not active.")

    if is_override:
        if not override_reason or not recorded_by:
            raise AttendanceEligibilityError(
                "OVERRIDE_REQUIRES_REASON", "Manual override requires both a reason and the staff member performing it."
            )
    else:
        if not _member_has_active_membership(member, at):
            raise AttendanceEligibilityError(
                "MEMBERSHIP_NOT_ACTIVE", "This member does not have an active membership covering today."
            )
        if not _member_may_use_branch(member, branch):
            raise AttendanceEligibilityError(
                "BRANCH_NOT_PERMITTED", "This member is not permitted to check in at this branch."
            )
        interval = _duplicate_interval_minutes(member)
        recent_cutoff = at - timedelta(minutes=interval)
        if Attendance.objects.filter(member=member, checkin_at__gte=recent_cutoff, checkin_at__lte=at).exists():
            raise AttendanceEligibilityError(
                "DUPLICATE_CHECKIN",
                f"This member already checked in within the last {interval} minutes.",
            )

    attendance = Attendance(
        organization=member.organization,
        member=member,
        branch=branch,
        checkin_at=at,
        method=method,
        device_id=device_id,
        recorded_by=recorded_by,
        override_reason=override_reason,
    )
    attendance.full_clean()
    attendance.save()
    if is_override:
        from audit.services import audit_log

        audit_log(
            organization=member.organization,
            actor=recorded_by,
            action="CHECKIN_OVERRIDE",
            resource_type="attendance.Attendance",
            resource_uuid=attendance.uuid,
            branch=branch,
            after={"method": method, "reason": override_reason},
        )
    return attendance
