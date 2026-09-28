import datetime
from decimal import Decimal

import factory

from members.tests.factories import MemberFactory
from memberships.models import FreezeRequest, Membership, MembershipPlan


class MembershipPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembershipPlan

    organization = factory.SubFactory("organizations.tests.factories.OrganizationFactory")
    name = factory.Sequence(lambda n: f"Plan {n}")
    duration_days = 30
    price = Decimal("2000.00")
    billing_frequency = MembershipPlan.BillingFrequency.MONTHLY
    freeze_allowed = True
    max_freeze_days = 15


class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Membership

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    plan = factory.SubFactory(MembershipPlanFactory, organization=factory.SelfAttribute("..member.organization"))
    start_date = factory.LazyFunction(datetime.date.today)
    end_date = factory.LazyAttribute(lambda o: o.start_date + datetime.timedelta(days=30))
    status = Membership.Status.ACTIVE
    price = Decimal("2000.00")


class FreezeRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FreezeRequest

    membership = factory.SubFactory(MembershipFactory)
    organization = factory.SelfAttribute("membership.organization")
    member = factory.SelfAttribute("membership.member")
    start_date = factory.LazyFunction(datetime.date.today)
    end_date = factory.LazyAttribute(lambda o: o.start_date + datetime.timedelta(days=5))
    reason = "Travel"
    notes = ""
    status = FreezeRequest.Status.PENDING
    requested_by = factory.SubFactory("accounts.tests.factories.UserFactory", role="MEMBER")
