"""Mandatory tenant-isolation coverage for attendance.Attendance (AGENTS.md §16.4)."""

import pytest

from attendance.models import Attendance
from attendance.tests.factories import AttendanceFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_attendance_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    from members.tests.factories import MemberFactory

    att_a = AttendanceFactory(member=MemberFactory(organization=org_a))
    att_b = AttendanceFactory(member=MemberFactory(organization=org_b))

    visible = Attendance.objects.for_organization(org_a)
    assert att_a in visible
    assert att_b not in visible
