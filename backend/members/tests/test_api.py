import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory, UserFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_owner_can_create_and_list_member():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    client = auth_client(owner)

    response = client.post(
        "/api/v1/members/",
        {
            "full_name": "Anita Rao",
            "phone": "+919876501111",
            "home_branch_id": str(branch.uuid),
            "joining_date": "2026-09-28",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data["data"]["full_name"] == "Anita Rao"
    assert response.data["data"]["member_code"].startswith("GYM-")

    listed = client.get("/api/v1/members/?search=Anita")
    assert listed.status_code == 200
    assert listed.data["meta"]["total"] == 1


def test_organization_a_cannot_read_organization_b_member():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    member_b = MemberFactory(organization=owner_b.organization, home_branch=BranchFactory(organization=owner_b.organization))

    response = auth_client(owner_a).get(f"/api/v1/members/{member_b.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_client_supplied_organization_id_is_ignored():
    owner = OwnerFactory()
    other = OrganizationFactory()
    branch = BranchFactory(organization=owner.organization)
    response = auth_client(owner).post(
        "/api/v1/members/",
        {
            "full_name": "Ignored Org",
            "phone": "+919876501112",
            "home_branch_id": str(branch.uuid),
            "joining_date": "2026-09-28",
            "organization_id": str(other.uuid),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["data"]["organization_id"] == str(owner.organization.uuid)


def test_staff_cannot_see_other_branch_member():
    org = OrganizationFactory()
    branch_a = BranchFactory(organization=org)
    branch_b = BranchFactory(organization=org)
    staff = UserFactory(organization=org, home_branch=branch_a, role="STAFF_ADMIN")
    hidden = MemberFactory(organization=org, home_branch=branch_b)

    response = auth_client(staff).get(f"/api/v1/members/{hidden.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_member_role_sees_only_own_profile():
    org = OrganizationFactory()
    branch = BranchFactory(organization=org)
    portal_user = UserFactory(organization=org, home_branch=branch, role="MEMBER")
    own = MemberFactory(organization=org, home_branch=branch, user=portal_user)
    MemberFactory(organization=org, home_branch=branch)

    listed = auth_client(portal_user).get("/api/v1/members/")
    assert listed.data["meta"]["total"] == 1
    assert listed.data["data"][0]["id"] == str(own.uuid)


def test_owner_provisions_portal_login_and_member_me():
    owner = OwnerFactory()
    member = MemberFactory(organization=owner.organization)
    provisioned = auth_client(owner).post(
        f"/api/v1/members/{member.uuid}/provision-login/",
        {"email": "priya.portal@example.com", "password": "MemberPass123!"},
        format="json",
    )
    assert provisioned.status_code == 200
    assert provisioned.data["data"]["has_portal_login"] is True
    from accounts.models import User

    portal_user = User.objects.get(email="priya.portal@example.com")
    me = auth_client(portal_user).get("/api/v1/members/me/")
    assert me.status_code == 200
    assert me.data["data"]["id"] == str(member.uuid)


def test_unauthenticated_member_list_is_401():
    from rest_framework.test import APIClient

    response = APIClient().get("/api/v1/members/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
