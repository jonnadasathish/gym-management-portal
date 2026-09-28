import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory, UserFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from crm.models import Lead
from crm.tests.factories import LeadFactory
from members.models import Member
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_convert_creates_member_in_same_org():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    lead = LeadFactory(
        organization=owner.organization,
        branch=branch,
        name="Anita Rao",
        phone="+919876509901",
    )

    response = auth_client(owner).post(f"/api/v1/crm/leads/{lead.uuid}/convert/")
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data["data"]["status"] == Lead.Status.CONVERTED

    lead.refresh_from_db()
    member = lead.converted_member
    assert member is not None
    assert member.organization_id == owner.organization_id
    assert member.full_name == "Anita Rao"
    assert member.phone == "+919876509901"
    assert member.home_branch_id == branch.id
    assert member.member_code.startswith("GYM-")
    assert Member.objects.for_organization(owner.organization).filter(pk=member.pk).exists()


def test_other_org_cannot_see_lead():
    owner = OwnerFactory()
    lead = LeadFactory()
    response = auth_client(owner).get(f"/api/v1/crm/leads/{lead.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_staff_cannot_see_other_branch_lead():
    org = OrganizationFactory()
    branch_a = BranchFactory(organization=org)
    branch_b = BranchFactory(organization=org)
    staff = UserFactory(organization=org, home_branch=branch_a, role="STAFF_ADMIN")
    hidden = LeadFactory(organization=org, branch=branch_b)

    response = auth_client(staff).get(f"/api/v1/crm/leads/{hidden.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
