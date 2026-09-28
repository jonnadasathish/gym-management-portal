import factory

from accounts.tests.factories import OwnerFactory
from data_migration.models import ImportJob
from organizations.tests.factories import OrganizationFactory


class ImportJobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImportJob

    organization = factory.SubFactory(OrganizationFactory)
    uploaded_by = factory.SubFactory(OwnerFactory, organization=factory.SelfAttribute("..organization"))
    entity_type = ImportJob.EntityType.MEMBERS
    status = ImportJob.Status.UPLOADED
    raw_csv = ""
