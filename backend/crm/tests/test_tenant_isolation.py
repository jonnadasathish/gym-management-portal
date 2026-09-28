"""Mandatory tenant-isolation coverage for crm.Lead (AGENTS.md §16.4)."""

import pytest

from crm.models import Lead
from crm.tests.factories import LeadFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_leads_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    lead_a = LeadFactory(organization=org_a)
    lead_b = LeadFactory(organization=org_b)

    visible = Lead.objects.for_organization(org_a)

    assert lead_a in visible
    assert lead_b not in visible


def test_organization_a_cannot_read_organization_b_lead_by_scoped_lookup():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    lead_b = LeadFactory(organization=org_b)

    with pytest.raises(Lead.DoesNotExist):
        Lead.objects.for_organization(org_a).get(pk=lead_b.pk)
