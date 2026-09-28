import pytest

from members.tests.factories import MemberFactory
from notifications.models import NotificationChannel, NotificationEventType, NotificationLog
from notifications.providers import ConsoleNotificationProvider, NotificationProvider
from notifications.services import enqueue_notification
from notifications.tests.factories import NotificationTemplateFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


class RecordingProvider(NotificationProvider):
    def __init__(self):
        self.calls = []

    def send(self, *, to, body, metadata):
        self.calls.append({"to": to, "body": body, "metadata": metadata})
        return "console-recorded"


def test_enqueue_creates_sent_log():
    org = OrganizationFactory()
    member = MemberFactory(organization=org)
    log = enqueue_notification(
        organization=org,
        event_type=NotificationEventType.MEMBERSHIP_CREATED,
        member=member,
    )
    assert log.status == NotificationLog.Status.SENT
    assert log.organization_id == org.id
    assert log.recipient_member_id == member.id
    assert log.provider_message_id.startswith("console-")
    assert log.sent_at is not None
    assert NotificationLog.objects.for_organization(org).filter(pk=log.pk).exists()


def test_enqueue_default_body_is_event_type():
    org = OrganizationFactory()
    provider = RecordingProvider()
    enqueue_notification(
        organization=org,
        event_type=NotificationEventType.PAYMENT_FAILED,
        provider=provider,
    )
    assert provider.calls[0]["body"] == NotificationEventType.PAYMENT_FAILED


def test_enqueue_renders_active_org_template():
    org = OrganizationFactory()
    NotificationTemplateFactory(
        organization=org,
        event_type=NotificationEventType.PAYMENT_SUCCESSFUL,
        channel=NotificationChannel.IN_APP,
        body="PAYMENT_SUCCESSFUL {amount}",
    )
    provider = RecordingProvider()
    enqueue_notification(
        organization=org,
        event_type=NotificationEventType.PAYMENT_SUCCESSFUL,
        context={"amount": "500"},
        provider=provider,
    )
    assert provider.calls[0]["body"] == "PAYMENT_SUCCESSFUL 500"


def test_enqueue_does_not_use_the_network(monkeypatch):
    def _blocked(*args, **kwargs):
        raise AssertionError("notifications must not use the network")

    monkeypatch.setattr("urllib.request.urlopen", _blocked)
    org = OrganizationFactory()
    log = enqueue_notification(
        organization=org,
        event_type=NotificationEventType.BIRTHDAY,
        channel=NotificationChannel.WHATSAPP,
    )
    assert log.status == NotificationLog.Status.SENT
    assert log.provider_message_id.startswith("console-")
    assert ConsoleNotificationProvider().send(to="", body="x", metadata={}).startswith("console-")
