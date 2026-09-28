import datetime

import factory

from branches.tests.factories import BranchFactory
from members.models import Member
from organizations.tests.factories import OrganizationFactory


class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Member

    organization = factory.SubFactory(OrganizationFactory)
    home_branch = factory.SubFactory(BranchFactory, organization=factory.SelfAttribute("..organization"))
    member_code = factory.Sequence(lambda n: f"GYM-{n:06d}")
    full_name = factory.Sequence(lambda n: f"Test Member {n}")
    phone = factory.Sequence(lambda n: f"+9198765{n:05d}")
    joining_date = factory.LazyFunction(datetime.date.today)
