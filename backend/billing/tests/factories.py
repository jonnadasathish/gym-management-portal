import datetime
from decimal import Decimal

import factory

from billing.models import Invoice, InvoiceLineItem
from members.tests.factories import MemberFactory


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    invoice_number = factory.Sequence(lambda n: f"INV-{n:06d}")
    issue_date = factory.LazyFunction(datetime.date.today)
    total = Decimal("2000.00")
    status = Invoice.Status.ISSUED


class InvoiceLineItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceLineItem

    invoice = factory.SubFactory(InvoiceFactory)
    description = "Monthly membership"
    quantity = Decimal("1.00")
    unit_price = Decimal("2000.00")
    tax_rate = Decimal("0.00")
    line_total = Decimal("2000.00")
