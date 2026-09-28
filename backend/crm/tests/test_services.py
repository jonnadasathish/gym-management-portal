import pytest

from crm.models import Lead
from crm.services import CRMStateError, convert_lead
from crm.tests.factories import LeadFactory
from members.models import Member

pytestmark = pytest.mark.django_db


def test_convert_lead_creates_member_in_same_organization():
    lead = LeadFactory(name="Priya Shah", phone="+919876509902")
    converted, member = convert_lead(lead_id=lead.id)
    assert converted.status == Lead.Status.CONVERTED
    assert member.organization_id == lead.organization_id
    assert member.full_name == "Priya Shah"
    assert member.phone == "+919876509902"
    assert member.home_branch_id == lead.branch_id
    assert Member.objects.for_organization(lead.organization).filter(pk=member.pk).exists()


def test_convert_lead_twice_is_rejected():
    lead = LeadFactory()
    convert_lead(lead_id=lead.id)
    with pytest.raises(CRMStateError) as exc:
        convert_lead(lead_id=lead.id)
    assert exc.value.code == "ALREADY_CONVERTED"
