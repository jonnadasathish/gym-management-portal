"""Mandatory tenant-isolation coverage for payments.Payment (AGENTS.md §16.4)."""

import pytest

from billing.tests.factories import InvoiceFactory
from members.tests.factories import MemberFactory
from organizations.tests.factories import OrganizationFactory
from payments.models import Payment, Subscription
from payments.tests.factories import PaymentFactory, SubscriptionFactory

pytestmark = pytest.mark.django_db


def test_payments_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    payment_a = PaymentFactory(invoice=InvoiceFactory(member=MemberFactory(organization=org_a)))
    payment_b = PaymentFactory(invoice=InvoiceFactory(member=MemberFactory(organization=org_b)))

    visible = Payment.objects.for_organization(org_a)
    assert payment_a in visible
    assert payment_b not in visible


def test_subscriptions_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    sub_a = SubscriptionFactory(member=MemberFactory(organization=org_a))
    sub_b = SubscriptionFactory(member=MemberFactory(organization=org_b))

    visible = Subscription.objects.for_organization(org_a)
    assert sub_a in visible
    assert sub_b not in visible
