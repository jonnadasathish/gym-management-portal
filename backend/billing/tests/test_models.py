from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from billing.models import Invoice
from billing.tests.factories import InvoiceFactory, InvoiceLineItemFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_invoice_number_unique_per_organization():
    org = OrganizationFactory()
    InvoiceFactory(member__organization=org, organization=org, invoice_number="INV-000001")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            InvoiceFactory(member__organization=org, organization=org, invoice_number="INV-000001")


def test_same_invoice_number_allowed_across_organizations():
    InvoiceFactory(invoice_number="INV-DUP")
    InvoiceFactory(invoice_number="INV-DUP")  # different org — must not raise


def test_recompute_totals_from_line_items():
    invoice = InvoiceFactory(discount=Decimal("100.00"))
    InvoiceLineItemFactory(invoice=invoice, quantity=Decimal("1"), unit_price=Decimal("2000.00"), tax_rate=Decimal("18.00"), line_total=Decimal("2360.00"))

    invoice.recompute_totals()

    assert invoice.subtotal == Decimal("2000.00")
    assert invoice.tax == Decimal("360.00")
    assert invoice.total == Decimal("2260.00")  # 2000 + 360 - 100 discount
