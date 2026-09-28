import factory

from branches.models import Branch
from organizations.tests.factories import OrganizationFactory


class BranchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Branch

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Sequence(lambda n: f"Branch {n}")
    status = Branch.Status.ACTIVE
