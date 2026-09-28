import datetime
from decimal import Decimal

import factory

from billing.tests.factories import InvoiceFactory
from members.tests.factories import MemberFactory
from memberships.tests.factories import MembershipPlanFactory
from payments.models import Payment, Subscription


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    invoice = factory.SubFactory(InvoiceFactory)
    organization = factory.SelfAttribute("invoice.organization")
    amount = Decimal("2000.00")
    method = Payment.Method.CASH
    status = Payment.Status.SUCCESSFUL


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    membership_plan = factory.SubFactory(
        MembershipPlanFactory, organization=factory.SelfAttribute("..member.organization")
    )
    gateway = "RAZORPAY"
    status = Subscription.Status.ACTIVE
    next_billing_date = factory.LazyFunction(lambda: datetime.date.today() + datetime.timedelta(days=30))
    retry_count = 0
