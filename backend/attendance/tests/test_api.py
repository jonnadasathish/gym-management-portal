import datetime

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from attendance.models import Attendance
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from memberships.tests.factories import MembershipFactory

pytestmark = pytest.mark.django_db


def test_staff_check_in_active_member():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member = MemberFactory(organization=owner.organization, home_branch=branch)
    MembershipFactory(member=member, organization=owner.organization)
    client = auth_client(owner)

    response = client.post(
        "/api/v1/attendance/check-in/",
        {
            "member_id": str(member.uuid),
            "branch_id": str(branch.uuid),
            "method": Attendance.Method.STAFF_SEARCH,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["data"]["member"] == str(member.uuid)


def test_check_in_rejects_ineligible_member():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member = MemberFactory(organization=owner.organization, home_branch=branch)
    response = auth_client(owner).post(
        "/api/v1/attendance/check-in/",
        {"member_id": str(member.uuid), "branch_id": str(branch.uuid)},
        format="json",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.data["error"]["code"] == "MEMBERSHIP_NOT_ACTIVE"


def test_other_org_member_cannot_be_checked_in():
    owner = OwnerFactory()
    other = MemberFactory()
    branch = BranchFactory(organization=owner.organization)
    response = auth_client(owner).post(
        "/api/v1/attendance/check-in/",
        {"member_id": str(other.uuid), "branch_id": str(branch.uuid)},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_staff_check_in_with_qr_payload():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member = MemberFactory(organization=owner.organization, home_branch=branch)
    MembershipFactory(member=member, organization=owner.organization)
    client = auth_client(owner)

    response = client.post(
        "/api/v1/attendance/check-in/",
        {
            "qr_payload": f"gymportal:member:{member.uuid}",
            "branch_id": str(branch.uuid),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["data"]["member"] == str(member.uuid)
    assert response.data["data"]["method"] == Attendance.Method.QR


def test_check_in_rejects_malformed_qr_payload():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    response = auth_client(owner).post(
        "/api/v1/attendance/check-in/",
        {"qr_payload": "not-a-valid-payload", "branch_id": str(branch.uuid)},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_check_in_rejects_other_org_qr_payload():
    owner = OwnerFactory()
    other = MemberFactory()
    branch = BranchFactory(organization=owner.organization)
    response = auth_client(owner).post(
        "/api/v1/attendance/check-in/",
        {
            "qr_payload": f"gymportal:member:{other.uuid}",
            "branch_id": str(branch.uuid),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
