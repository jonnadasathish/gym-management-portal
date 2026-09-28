"""Mandatory tenant-isolation coverage for notifications (AGENTS.md §16.4)."""

import pytest

from members.tests.factories import MemberFactory
from notifications.models import NotificationLog
from notifications.tests.factories import NotificationLogFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_notification_logs_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    log_a = NotificationLogFactory(organization=org_a, recipient_member=MemberFactory(organization=org_a))
    log_b = NotificationLogFactory(organization=org_b, recipient_member=MemberFactory(organization=org_b))

    visible = NotificationLog.objects.for_organization(org_a)
    assert log_a in visible
    assert log_b not in visible
