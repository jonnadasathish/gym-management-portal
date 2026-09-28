import datetime

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory, UserFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from members.models import Member
from members.tests.factories import MemberFactory
from memberships.models import FreezeRequest, Membership
from memberships.tests.factories import MembershipFactory, MembershipPlanFactory

pytestmark = pytest.mark.django_db


def test_owner_sells_membership_and_freezes():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member = MemberFactory(organization=owner.organization, home_branch=branch, status=Member.Status.INACTIVE)
    plan = MembershipPlanFactory(organization=owner.organization)
    client = auth_client(owner)

    created = client.post(
        "/api/v1/memberships/",
        {
            "member_id": str(member.uuid),
            "plan_id": str(plan.uuid),
            "start_date": "2026-09-01",
        },
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED
    membership_id = created.data["data"]["id"]
    assert created.data["data"]["status"] == Membership.Status.ACTIVE
    member.refresh_from_db()
    assert member.status == Member.Status.ACTIVE

    frozen = client.post(
        f"/api/v1/memberships/{membership_id}/freeze/",
        {"start_date": "2026-09-10", "end_date": "2026-09-12", "reason": "Travel"},
        format="json",
    )
    assert frozen.status_code == 200
    assert frozen.data["data"]["status"] == Membership.Status.FROZEN
    assert len(frozen.data["data"]["freezes"]) == 1


def test_other_org_cannot_read_membership():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    member_b = MemberFactory(
        organization=owner_b.organization,
        home_branch=BranchFactory(organization=owner_b.organization),
    )
    membership = MembershipFactory(member=member_b, organization=owner_b.organization)

    response = auth_client(owner_a).get(f"/api/v1/memberships/{membership.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def _member_with_membership(*, org, branch):
    member_user = UserFactory(role="MEMBER", organization=org, home_branch=branch)
    member = MemberFactory(organization=org, home_branch=branch, user=member_user)
    membership = MembershipFactory(member=member, organization=org)
    return member_user, member, membership


def test_member_creates_pending_freeze_request():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member_user, member, membership = _member_with_membership(org=owner.organization, branch=branch)

    response = auth_client(member_user).post(
        f"/api/v1/memberships/{membership.uuid}/request-freeze/",
        {
            "start_date": "2026-10-01",
            "end_date": "2026-10-10",
            "reason": "Travel",
            "notes": "Family trip",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    payload = response.data["data"]
    assert payload["status"] == FreezeRequest.Status.PENDING
    assert payload["start_date"] == "2026-10-01"
    assert payload["end_date"] == "2026-10-10"
    assert payload["reason"] == "Travel"

    membership.refresh_from_db()
    assert membership.status == Membership.Status.ACTIVE

    listed = auth_client(owner).get(f"/api/v1/memberships/freeze-requests/?member={member.uuid}")
    assert listed.status_code == 200
    assert listed.data["meta"]["total"] == 1
    assert listed.data["data"][0]["id"] == payload["id"]

    nested = auth_client(member_user).get(f"/api/v1/memberships/{membership.uuid}/")
    assert nested.status_code == 200
    assert len(nested.data["data"]["freeze_requests"]) == 1
    assert nested.data["data"]["freeze_requests"][0]["status"] == FreezeRequest.Status.PENDING


def test_request_freeze_requires_dates():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member_user, _, membership = _member_with_membership(org=owner.organization, branch=branch)

    response = auth_client(member_user).post(
        f"/api/v1/memberships/{membership.uuid}/request-freeze/",
        {"reason": "Travel"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_staff_cannot_request_freeze():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    staff = UserFactory(role="STAFF_ADMIN", organization=owner.organization, home_branch=branch)
    _, _, membership = _member_with_membership(org=owner.organization, branch=branch)

    response = auth_client(staff).post(
        f"/api/v1/memberships/{membership.uuid}/request-freeze/",
        {"start_date": "2026-10-01", "end_date": "2026-10-10", "reason": "Travel"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_staff_approve_freezes_membership_second_approve_rejected():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    staff = UserFactory(role="STAFF_ADMIN", organization=owner.organization, home_branch=branch)
    member_user, member, membership = _member_with_membership(org=owner.organization, branch=branch)

    created = auth_client(member_user).post(
        f"/api/v1/memberships/{membership.uuid}/request-freeze/",
        {"start_date": "2026-10-01", "end_date": "2026-10-10", "reason": "Travel"},
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED
    request_id = created.data["data"]["id"]

    approved = auth_client(staff).post(
        f"/api/v1/memberships/freeze-requests/{request_id}/approve/",
        {},
        format="json",
    )
    assert approved.status_code == 200, approved.data
    assert approved.data["data"]["status"] == FreezeRequest.Status.APPROVED

    membership.refresh_from_db()
    member.refresh_from_db()
    assert membership.status == Membership.Status.FROZEN
    assert member.status == Member.Status.FROZEN
    assert membership.freezes.count() == 1

    second = auth_client(staff).post(
        f"/api/v1/memberships/freeze-requests/{request_id}/approve/",
        {},
        format="json",
    )
    assert second.status_code == status.HTTP_409_CONFLICT
    membership.refresh_from_db()
    assert membership.freezes.count() == 1


def test_staff_reject_does_not_freeze():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    staff = UserFactory(role="STAFF_ADMIN", organization=owner.organization, home_branch=branch)
    member_user, _, membership = _member_with_membership(org=owner.organization, branch=branch)

    created = auth_client(member_user).post(
        f"/api/v1/memberships/{membership.uuid}/request-freeze/",
        {"start_date": "2026-10-01", "end_date": "2026-10-10", "reason": "Travel"},
        format="json",
    )
    request_id = created.data["data"]["id"]

    rejected = auth_client(staff).post(
        f"/api/v1/memberships/freeze-requests/{request_id}/reject/",
        {},
        format="json",
    )
    assert rejected.status_code == 200
    assert rejected.data["data"]["status"] == FreezeRequest.Status.REJECTED
    membership.refresh_from_db()
    assert membership.status == Membership.Status.ACTIVE
    assert membership.freezes.count() == 0


def test_other_org_cannot_approve_freeze_request():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    branch_b = BranchFactory(organization=owner_b.organization)
    member_user, _, membership = _member_with_membership(org=owner_b.organization, branch=branch_b)

    created = auth_client(member_user).post(
        f"/api/v1/memberships/{membership.uuid}/request-freeze/",
        {"start_date": "2026-10-01", "end_date": "2026-10-10", "reason": "Travel"},
        format="json",
    )
    request_id = created.data["data"]["id"]

    listed = auth_client(owner_a).get("/api/v1/memberships/freeze-requests/")
    assert listed.status_code == 200
    assert listed.data["meta"]["total"] == 0

    approve = auth_client(owner_a).post(
        f"/api/v1/memberships/freeze-requests/{request_id}/approve/",
        {},
        format="json",
    )
    assert approve.status_code == status.HTTP_404_NOT_FOUND
    membership.refresh_from_db()
    assert membership.status == Membership.Status.ACTIVE
