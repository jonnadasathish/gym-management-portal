from datetime import timedelta
from decimal import Decimal

import factory
from django.utils import timezone

from accounts.tests.factories import UserFactory
from members.tests.factories import MemberFactory
from pt.models import PTPackage, PTSession


class PTPackageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PTPackage

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    trainer = factory.SubFactory(UserFactory, role="TRAINER", organization=factory.SelfAttribute("..organization"))
    plan_name = "10 sessions"
    sessions_purchased = 10
    sessions_consumed = 0
    price = Decimal("15000.00")


class PTSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PTSession

    package = factory.SubFactory(PTPackageFactory)
    organization = factory.SelfAttribute("package.organization")
    member = factory.SelfAttribute("package.member")
    trainer = factory.SelfAttribute("package.trainer")
    scheduled_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
    duration_minutes = 60
    status = PTSession.Status.SCHEDULED
