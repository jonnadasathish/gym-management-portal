import uuid

import factory

from accounts.tests.factories import UserFactory
from audit.models import AuditLog
from organizations.tests.factories import OrganizationFactory


class AuditLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditLog

    organization = factory.SubFactory(OrganizationFactory)
    actor = factory.SubFactory(UserFactory, organization=factory.SelfAttribute("..organization"))
    action = "TEST_ACTION"
    resource_type = "member"
    resource_uuid = factory.LazyFunction(uuid.uuid4)
    system_initiated = False
    request_id = ""
