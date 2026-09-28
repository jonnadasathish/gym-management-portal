"""Mandatory tenant-isolation coverage for billing.Invoice (AGENTS.md §16.4)."""

import pytest

from billing.models import Invoice
from billing.tests.factories import InvoiceFactory
from members.tests.factories import MemberFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_invoices_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    invoice_a = InvoiceFactory(member=MemberFactory(organization=org_a))
    invoice_b = InvoiceFactory(member=MemberFactory(organization=org_b))

    visible = Invoice.objects.for_organization(org_a)
    assert invoice_a in visible
    assert invoice_b not in visible
