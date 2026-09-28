import factory

from notifications.models import NotificationChannel, NotificationEventType, NotificationLog, NotificationTemplate
from organizations.tests.factories import OrganizationFactory


class NotificationTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NotificationTemplate

    organization = factory.SubFactory(OrganizationFactory)
    event_type = NotificationEventType.MEMBERSHIP_CREATED
    channel = NotificationChannel.IN_APP
    body = "MEMBERSHIP_CREATED"
    is_active = True


class NotificationLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NotificationLog

    organization = factory.SubFactory(OrganizationFactory)
    event_type = NotificationEventType.MEMBERSHIP_CREATED
    channel = NotificationChannel.IN_APP
    status = NotificationLog.Status.SENT
    payload = factory.LazyFunction(dict)
