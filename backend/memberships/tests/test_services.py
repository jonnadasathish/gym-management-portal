import datetime
from decimal import Decimal

import pytest

from members.models import Member
from members.tests.factories import MemberFactory
from memberships.models import Membership, MembershipFreeze
from memberships.services import (
    MembershipStateError,
    apply_freeze,
    expire_overdue_memberships,
    renew_membership,
    sync_member_status,
    unfreeze_membership,
)
from memberships.tests.factories import MembershipFactory, MembershipPlanFactory
from organizations.models import Organization

pytestmark = pytest.mark.django_db


def test_apply_freeze_extends_end_date_under_extend_policy():
    membership = MembershipFactory(
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
    )
    membership.organization.freeze_policy = Organization.FreezePolicy.EXTEND_BY_FREEZE_DAYS
    membership.organization.save()

    updated, freeze = apply_freeze(
        membership_id=membership.id,
        start_date=datetime.date(2026, 1, 10),
        end_date=datetime.date(2026, 1, 19),  # 10 days inclusive
        reason="Travel",
        requested_by=None,
    )

    assert updated.status == Membership.Status.FROZEN
    assert updated.end_date == datetime.date(2026, 2, 10)  # 31 Jan + 10 days
    assert freeze.revised_end_date == updated.end_date
    assert MembershipFreeze.objects.filter(membership=membership).count() == 1


def test_apply_freeze_does_not_extend_under_pause_no_extend_policy():
    membership = MembershipFactory(
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
    )
    membership.organization.freeze_policy = Organization.FreezePolicy.PAUSE_NO_EXTEND
    membership.organization.save()

    updated, _ = apply_freeze(
        membership_id=membership.id,
        start_date=datetime.date(2026, 1, 10),
        end_date=datetime.date(2026, 1, 19),
        reason="Travel",
        requested_by=None,
    )

    assert updated.end_date == datetime.date(2026, 1, 31)  # unchanged


def test_apply_freeze_rejects_non_active_membership():
    membership = MembershipFactory(status=Membership.Status.FROZEN)
    with pytest.raises(MembershipStateError):
        apply_freeze(
            membership_id=membership.id,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=5),
            reason="x",
            requested_by=None,
        )


def test_apply_freeze_rejects_when_plan_disallows_freeze():
    plan = MembershipPlanFactory(freeze_allowed=False)
    membership = MembershipFactory(plan=plan)
    with pytest.raises(MembershipStateError):
        apply_freeze(
            membership_id=membership.id,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=5),
            reason="x",
            requested_by=None,
        )


def test_apply_freeze_rejects_when_exceeding_max_freeze_days():
    plan = MembershipPlanFactory(freeze_allowed=True, max_freeze_days=5)
    membership = MembershipFactory(plan=plan)
    with pytest.raises(MembershipStateError):
        apply_freeze(
            membership_id=membership.id,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=10),
            reason="x",
            requested_by=None,
        )


def test_freeze_history_is_never_deleted_by_unfreeze():
    membership = MembershipFactory(
        start_date=datetime.date(2026, 1, 1), end_date=datetime.date(2026, 1, 31)
    )
    apply_freeze(
        membership_id=membership.id,
        start_date=datetime.date(2026, 1, 10),
        end_date=datetime.date(2026, 1, 15),
        reason="Injury",
        requested_by=None,
    )
    unfrozen = unfreeze_membership(membership_id=membership.id)

    assert unfrozen.status == Membership.Status.ACTIVE
    assert MembershipFreeze.objects.filter(membership=membership).count() == 1  # still there


def test_unfreeze_rejects_non_frozen_membership():
    membership = MembershipFactory(status=Membership.Status.ACTIVE)
    with pytest.raises(MembershipStateError):
        unfreeze_membership(membership_id=membership.id)


def test_renew_preserves_old_membership_row_and_creates_new_one():
    old_membership = MembershipFactory(status=Membership.Status.ACTIVE)
    member = old_membership.member
    new_plan = MembershipPlanFactory(organization=member.organization)

    new_membership = renew_membership(
        membership_id=old_membership.id,
        new_plan=new_plan,
        new_start_date=old_membership.end_date + datetime.timedelta(days=1),
        new_end_date=old_membership.end_date + datetime.timedelta(days=31),
        price=Decimal("2200.00"),
        discount=Decimal("0.00"),
        created_by=None,
    )

    old_membership.refresh_from_db()
    assert old_membership.status == Membership.Status.EXPIRED  # preserved, not deleted
    assert new_membership.status == Membership.Status.ACTIVE
    assert new_membership.member_id == member.id
    assert Membership.objects.filter(member=member).count() == 2  # full history retained


def test_expire_overdue_memberships_expires_active_ending_yesterday():
    as_of = datetime.datetime(2026, 9, 28, 12, 0, tzinfo=datetime.timezone.utc)
    membership = MembershipFactory(
        status=Membership.Status.ACTIVE,
        start_date=datetime.date(2026, 8, 1),
        end_date=datetime.date(2026, 9, 27),
    )

    expired = expire_overdue_memberships(as_of=as_of)

    membership.refresh_from_db()
    assert membership.status == Membership.Status.EXPIRED
    assert [row.pk for row in expired] == [membership.pk]


def test_expire_overdue_memberships_leaves_frozen_alone():
    as_of = datetime.datetime(2026, 9, 28, 12, 0, tzinfo=datetime.timezone.utc)
    frozen = MembershipFactory(
        status=Membership.Status.FROZEN,
        start_date=datetime.date(2026, 8, 1),
        end_date=datetime.date(2026, 9, 27),
    )

    expired = expire_overdue_memberships(as_of=as_of)

    frozen.refresh_from_db()
    assert frozen.status == Membership.Status.FROZEN
    assert expired == []


def test_sync_member_status_no_memberships_sets_inactive():
    member = MemberFactory(status=Member.Status.ACTIVE)
    sync_member_status(member)
    member.refresh_from_db()
    assert member.status == Member.Status.INACTIVE


def test_sync_member_status_follows_latest_membership():
    member = MemberFactory(status=Member.Status.INACTIVE)
    MembershipFactory(
        member=member,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
        status=Membership.Status.EXPIRED,
    )
    MembershipFactory(
        member=member,
        start_date=datetime.date(2026, 2, 1),
        end_date=datetime.date(2026, 3, 3),
        status=Membership.Status.ACTIVE,
    )
    sync_member_status(member)
    member.refresh_from_db()
    assert member.status == Member.Status.ACTIVE


def test_sync_member_status_expired_when_latest_is_expired():
    member = MemberFactory(status=Member.Status.ACTIVE)
    MembershipFactory(
        member=member,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
        status=Membership.Status.ACTIVE,
    )
    MembershipFactory(
        member=member,
        start_date=datetime.date(2026, 2, 1),
        end_date=datetime.date(2026, 2, 28),
        status=Membership.Status.EXPIRED,
    )
    sync_member_status(member)
    member.refresh_from_db()
    assert member.status == Member.Status.EXPIRED


def test_sync_member_status_frozen_from_latest():
    member = MemberFactory()
    MembershipFactory(member=member, status=Membership.Status.FROZEN)
    sync_member_status(member)
    member.refresh_from_db()
    assert member.status == Member.Status.FROZEN


def test_apply_freeze_syncs_member_status_to_frozen():
    membership = MembershipFactory(
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
    )
    apply_freeze(
        membership_id=membership.id,
        start_date=datetime.date(2026, 1, 10),
        end_date=datetime.date(2026, 1, 15),
        reason="Injury",
        requested_by=None,
    )
    membership.member.refresh_from_db()
    assert membership.member.status == Member.Status.FROZEN


def test_unfreeze_syncs_member_status_to_active():
    membership = MembershipFactory(
        start_date=datetime.date(2026, 1, 1), end_date=datetime.date(2026, 1, 31)
    )
    apply_freeze(
        membership_id=membership.id,
        start_date=datetime.date(2026, 1, 10),
        end_date=datetime.date(2026, 1, 15),
        reason="Injury",
        requested_by=None,
    )
    unfreeze_membership(membership_id=membership.id)
    membership.member.refresh_from_db()
    assert membership.member.status == Member.Status.ACTIVE


def test_renew_syncs_member_status_to_active():
    old_membership = MembershipFactory(status=Membership.Status.EXPIRED)
    member = old_membership.member
    member.status = Member.Status.EXPIRED
    member.save(update_fields=["status"])
    new_plan = MembershipPlanFactory(organization=member.organization)

    renew_membership(
        membership_id=old_membership.id,
        new_plan=new_plan,
        new_start_date=old_membership.end_date + datetime.timedelta(days=1),
        new_end_date=old_membership.end_date + datetime.timedelta(days=31),
        price=Decimal("2200.00"),
        discount=Decimal("0.00"),
        created_by=None,
    )
    member.refresh_from_db()
    assert member.status == Member.Status.ACTIVE


def test_expire_overdue_memberships_syncs_member_status():
    as_of = datetime.datetime(2026, 9, 28, 12, 0, tzinfo=datetime.timezone.utc)
    membership = MembershipFactory(
        status=Membership.Status.ACTIVE,
        start_date=datetime.date(2026, 8, 1),
        end_date=datetime.date(2026, 9, 27),
    )

    expire_overdue_memberships(as_of=as_of)

    membership.member.refresh_from_db()
    assert membership.member.status == Member.Status.EXPIRED
