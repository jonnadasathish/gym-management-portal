import factory

from branches.tests.factories import BranchFactory
from crm.models import Lead, LeadActivity
from organizations.tests.factories import OrganizationFactory


class LeadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lead

    organization = factory.SubFactory(OrganizationFactory)
    branch = factory.SubFactory(BranchFactory, organization=factory.SelfAttribute("..organization"))
    name = factory.Sequence(lambda n: f"Lead {n}")
    phone = factory.Sequence(lambda n: f"+9198700{n:05d}")
    status = Lead.Status.NEW


class LeadActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LeadActivity

    lead = factory.SubFactory(LeadFactory)
    organization = factory.SelfAttribute("lead.organization")
    activity_type = "NOTE"
    notes = ""
