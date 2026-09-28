import datetime

import pytest
from django.utils import timezone

from accounts.tests.factories import UserFactory
from attendance.models import Attendance
from attendance.services import AttendanceEligibilityError, check_in
from branches.models import BranchAccess
from branches.tests.factories import BranchFactory
from members.tests.factories import MemberFactory
from memberships.tests.factories import MembershipFactory

pytestmark = pytest.mark.django_db


def _active_member():
    member = MemberFactory()
    MembershipFactory(
        member=member,
        start_date=timezone.now().date() - datetime.timedelta(days=5),
        end_date=timezone.now().date() + datetime.timedelta(days=25),
    )
    return member


def test_check_in_succeeds_for_active_member_at_home_branch():
    member = _active_member()
    attendance = check_in(member=member, branch=member.home_branch, method=Attendance.Method.QR)
    assert attendance.pk is not None
    assert attendance.method == Attendance.Method.QR


def test_check_in_rejects_member_without_active_membership():
    member = MemberFactory()  # no membership at all
    with pytest.raises(AttendanceEligibilityError) as exc:
        check_in(member=member, branch=member.home_branch, method=Attendance.Method.QR)
    assert exc.value.code == "MEMBERSHIP_NOT_ACTIVE"


def test_check_in_rejects_unpermitted_branch():
    member = _active_member()
    other_branch = BranchFactory(organization=member.organization)
    with pytest.raises(AttendanceEligibilityError) as exc:
        check_in(member=member, branch=other_branch, method=Attendance.Method.QR)
    assert exc.value.code == "BRANCH_NOT_PERMITTED"


def test_check_in_allowed_at_granted_branch():
    member = _active_member()
    other_branch = BranchFactory(organization=member.organization)
    BranchAccess.objects.create(member=member, branch=other_branch)

    attendance = check_in(member=member, branch=other_branch, method=Attendance.Method.QR)
    assert attendance.branch_id == other_branch.id


def test_duplicate_checkin_within_window_is_rejected():
    member = _active_member()
    check_in(member=member, branch=member.home_branch, method=Attendance.Method.QR)

    with pytest.raises(AttendanceEligibilityError) as exc:
        check_in(member=member, branch=member.home_branch, method=Attendance.Method.QR)
    assert exc.value.code == "DUPLICATE_CHECKIN"


def test_checkin_allowed_again_after_interval_passes():
    member = _active_member()
    earlier = timezone.now() - datetime.timedelta(minutes=200)
    check_in(member=member, branch=member.home_branch, method=Attendance.Method.QR, at=earlier)

    attendance = check_in(member=member, branch=member.home_branch, method=Attendance.Method.QR)
    assert attendance.pk is not None


def test_manual_override_bypasses_branch_and_duplicate_checks_but_requires_reason_and_staff():
    member = _active_member()
    other_branch = BranchFactory(organization=member.organization)  # not permitted normally
    staff = UserFactory(organization=member.organization)

    with pytest.raises(AttendanceEligibilityError) as exc:
        check_in(member=member, branch=other_branch, method=Attendance.Method.MANUAL_OVERRIDE)
    assert exc.value.code == "OVERRIDE_REQUIRES_REASON"

    attendance = check_in(
        member=member,
        branch=other_branch,
        method=Attendance.Method.MANUAL_OVERRIDE,
        override_reason="Trainer vouched for member; card not scanning.",
        recorded_by=staff,
    )
    assert attendance.override_reason
    assert attendance.recorded_by_id == staff.id


def test_soft_deleted_member_cannot_check_in_even_with_override():
    member = _active_member()
    member.soft_delete()
    staff = UserFactory(organization=member.organization)

    with pytest.raises(AttendanceEligibilityError) as exc:
        check_in(
            member=member,
            branch=member.home_branch,
            method=Attendance.Method.MANUAL_OVERRIDE,
            override_reason="test",
            recorded_by=staff,
        )
    assert exc.value.code == "ACCOUNT_BLOCKED"
