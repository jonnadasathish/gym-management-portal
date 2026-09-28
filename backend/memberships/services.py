"""Membership lifecycle business logic (AGENTS.md §19, §14 layering rule:
business logic lives here, not in views/serializers).

IMPORTANT — freeze policy caveat (OQ-005, PROJECT_CONTEXT.md §38, still
OPEN): the two named policies below (`EXTEND_BY_FREEZE_DAYS`,
`PAUSE_NO_EXTEND`) and their arithmetic are a reasonable, documented
implementation of what the PRD already describes ("the system must
calculate revised expiry according to configured freeze policy"). WHICH
policy is the correct *default* for a new organization is explicitly not
yet approved — do not treat `Organization.freeze_policy`'s current schema
default as a finalized business decision. This is recorded here and in
`PROJECT_CONTEXT.md` rather than silently assumed.

TODO (tracked, not forgotten): once the `audit` app exists, every call to
`apply_freeze` / `renew_membership` should also write an `AuditLog` entry
(AGENTS.md §17.6 — membership freeze and renewal are explicitly
audit-sensitive actions). Not yet wired because `audit` is a later
bounded task.
"""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from members.models import Member

from .models import FreezeRequest, Membership, MembershipFreeze


class MembershipStateError(Exception):
    """Raised when an operation is attempted against a membership in an
    incompatible state (e.g. freezing an already-frozen membership)."""


@transaction.atomic
def apply_freeze(*, membership_id, start_date, end_date, reason, requested_by, notes=""):
    """Freeze a membership and recompute its end_date per the
    organization's configured freeze policy (AGENTS.md §19.1, DEC-020
    concurrency: locks the membership row for the duration of the
    transaction so a concurrent freeze/renewal cannot race with this one).
    """

    membership = Membership.objects.select_for_update().select_related(
        "organization", "plan", "member"
    ).get(pk=membership_id)

    if membership.status != Membership.Status.ACTIVE:
        raise MembershipStateError(
            f"Cannot freeze a membership in status {membership.status!r}; must be ACTIVE."
        )
    if not membership.plan.freeze_allowed:
        raise MembershipStateError("This membership's plan does not allow freezing.")
    if end_date < start_date:
        raise ValidationError("Freeze end_date cannot be before start_date.")

    freeze_days = (end_date - start_date).days + 1

    if membership.plan.max_freeze_days is not None and freeze_days > membership.plan.max_freeze_days:
        raise MembershipStateError(
            f"Freeze of {freeze_days} days exceeds the plan's max_freeze_days "
            f"({membership.plan.max_freeze_days})."
        )

    policy = membership.organization.freeze_policy
    if policy == membership.organization.__class__.FreezePolicy.EXTEND_BY_FREEZE_DAYS:
        new_end_date = membership.end_date + timedelta(days=freeze_days)
    elif policy == membership.organization.__class__.FreezePolicy.PAUSE_NO_EXTEND:
        new_end_date = membership.end_date
    else:  # pragma: no cover - defensive, all enum values handled above
        raise MembershipStateError(f"Unknown freeze policy: {policy!r}")

    freeze = MembershipFreeze.objects.create(
        membership=membership,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        notes=notes,
        requested_by=requested_by,
        revised_end_date=new_end_date,
    )

    membership.status = Membership.Status.FROZEN
    membership.end_date = new_end_date
    membership.full_clean()
    membership.save(update_fields=["status", "end_date", "updated_at"])

    from audit.services import audit_log

    audit_log(
        organization=membership.organization,
        actor=requested_by,
        action="MEMBERSHIP_FREEZE",
        resource_type="memberships.Membership",
        resource_uuid=membership.uuid,
        after={"end_date": str(new_end_date), "reason": reason},
    )

    _enqueue_freeze_approved_notification(membership)
    sync_member_status(membership.member)
    return membership, freeze


@transaction.atomic
def unfreeze_membership(*, membership_id):
    """Return a frozen membership to ACTIVE. Does not delete freeze
    history (AGENTS.md §19.1/§59.4 — normal staff must not delete freeze
    records; this function never deletes, only transitions status)."""

    membership = Membership.objects.select_for_update().get(pk=membership_id)
    if membership.status != Membership.Status.FROZEN:
        raise MembershipStateError(
            f"Cannot unfreeze a membership in status {membership.status!r}; must be FROZEN."
        )
    membership.status = Membership.Status.ACTIVE
    membership.save(update_fields=["status", "updated_at"])
    from audit.services import audit_log

    audit_log(
        organization=membership.organization,
        action="MEMBERSHIP_UNFREEZE",
        resource_type="memberships.Membership",
        resource_uuid=membership.uuid,
        system_initiated=True,
    )
    sync_member_status(membership.member)
    return membership


@transaction.atomic
def renew_membership(*, membership_id, new_plan, new_start_date, new_end_date, price, discount, created_by):
    """Create a NEW Membership row for the renewal. Never mutates or
    deletes the prior membership row (AGENTS.md §19.3/§59.3 — renewal must
    preserve historical membership records)."""

    old_membership = Membership.objects.select_for_update().get(pk=membership_id)

    if old_membership.status not in (Membership.Status.ACTIVE, Membership.Status.EXPIRED):
        raise MembershipStateError(
            f"Cannot renew a membership in status {old_membership.status!r}."
        )

    old_membership.status = Membership.Status.EXPIRED
    old_membership.save(update_fields=["status", "updated_at"])

    new_membership = Membership.objects.create(
        organization=old_membership.organization,
        member=old_membership.member,
        plan=new_plan,
        start_date=new_start_date,
        end_date=new_end_date,
        status=Membership.Status.ACTIVE,
        price=price,
        discount=discount,
        created_by=created_by,
    )
    _enqueue_membership_created_notification(new_membership)
    sync_member_status(new_membership.member)
    return new_membership


def expire_overdue_memberships(*, as_of=None):
    """Mark ACTIVE memberships whose end_date is already past as EXPIRED.

    REQ-023: membership status is date-derived for the overdue ACTIVE case.
    Does not touch FROZEN or CANCELLED rows and does not apply freeze arithmetic.
    """

    as_of = as_of or timezone.now()
    expired = []
    affected_members = {}
    for membership in Membership.objects.select_related("member").filter(
        status=Membership.Status.ACTIVE,
        end_date__lt=as_of.date(),
    ):
        membership.status = Membership.Status.EXPIRED
        membership.save(update_fields=["status", "updated_at"])
        expired.append(membership)
        affected_members[membership.member_id] = membership.member
    for member in affected_members.values():
        sync_member_status(member)
    return expired


def sync_member_status(member):
    """Set Member.status from the latest membership (REQ-023).

    Latest membership is ordered by -start_date, -id. Mapping:
    - ACTIVE → Member.ACTIVE
    - FROZEN → Member.FROZEN
    - EXPIRED with no later ACTIVE/FROZEN → Member.EXPIRED
    - no memberships → Member.INACTIVE
    """

    latest = (
        Membership.objects.filter(member=member)
        .order_by("-start_date", "-id")
        .first()
    )
    if latest is None:
        new_status = Member.Status.INACTIVE
    elif latest.status == Membership.Status.ACTIVE:
        new_status = Member.Status.ACTIVE
    elif latest.status == Membership.Status.FROZEN:
        new_status = Member.Status.FROZEN
    elif latest.status == Membership.Status.EXPIRED:
        # `latest` is already -start_date, -id, so no later ACTIVE/FROZEN exists.
        new_status = Member.Status.EXPIRED
    else:
        # CANCELLED (or any other latest state) is not a live membership.
        new_status = Member.Status.INACTIVE

    if member.status != new_status:
        member.status = new_status
        member.save(update_fields=["status", "updated_at"])
    return member


def create_freeze_request(*, membership, requested_by, start_date, end_date, reason, notes=""):
    """Create a PENDING freeze request. Does not call apply_freeze."""

    freeze_request = FreezeRequest(
        organization=membership.organization,
        membership=membership,
        member=membership.member,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        notes=notes,
        status=FreezeRequest.Status.PENDING,
        requested_by=requested_by,
    )
    freeze_request.full_clean()
    freeze_request.save()
    return freeze_request


@transaction.atomic
def approve_freeze_request(*, freeze_request_id, reviewed_by):
    """Human approve only: apply_freeze with the request's dates/reason,
    requested_by=the member user who submitted it, then mark APPROVED."""

    freeze_request = (
        FreezeRequest.objects.select_for_update()
        .select_related("membership", "member", "requested_by")
        .get(pk=freeze_request_id)
    )
    if freeze_request.status != FreezeRequest.Status.PENDING:
        raise MembershipStateError(
            f"Cannot approve a freeze request in status {freeze_request.status!r}; must be PENDING."
        )
    apply_freeze(
        membership_id=freeze_request.membership_id,
        start_date=freeze_request.start_date,
        end_date=freeze_request.end_date,
        reason=freeze_request.reason,
        notes=freeze_request.notes,
        requested_by=freeze_request.requested_by,
    )
    freeze_request.status = FreezeRequest.Status.APPROVED
    freeze_request.reviewed_by = reviewed_by
    freeze_request.save(update_fields=["status", "reviewed_by", "updated_at"])
    return freeze_request


@transaction.atomic
def reject_freeze_request(*, freeze_request_id, reviewed_by):
    """Mark REJECTED. Does not call apply_freeze."""

    freeze_request = FreezeRequest.objects.select_for_update().get(pk=freeze_request_id)
    if freeze_request.status != FreezeRequest.Status.PENDING:
        raise MembershipStateError(
            f"Cannot reject a freeze request in status {freeze_request.status!r}; must be PENDING."
        )
    freeze_request.status = FreezeRequest.Status.REJECTED
    freeze_request.reviewed_by = reviewed_by
    freeze_request.save(update_fields=["status", "reviewed_by", "updated_at"])
    return freeze_request


def _enqueue_freeze_approved_notification(membership):
    """FREEZE_APPROVED is recorded after commit so notify failure cannot undo the freeze."""

    def _notify():
        try:
            from notifications.models import NotificationChannel, NotificationEventType
            from notifications.services import enqueue_notification

            enqueue_notification(
                organization=membership.organization,
                member=membership.member,
                event_type=NotificationEventType.FREEZE_APPROVED,
                channel=NotificationChannel.IN_APP,
                context={"membership_id": str(membership.uuid)},
            )
        except Exception:
            pass

    transaction.on_commit(_notify)


def _enqueue_membership_created_notification(membership):
    """MEMBERSHIP_CREATED is recorded after commit so notify failure cannot undo the membership."""

    def _notify():
        try:
            from notifications.models import NotificationChannel, NotificationEventType
            from notifications.services import enqueue_notification

            enqueue_notification(
                organization=membership.organization,
                member=membership.member,
                event_type=NotificationEventType.MEMBERSHIP_CREATED,
                channel=NotificationChannel.IN_APP,
                context={"membership_id": str(membership.uuid)},
            )
        except Exception:
            pass

    transaction.on_commit(_notify)
