import uuid

import pytest

from accounts.tests.factories import OwnerFactory
from audit.models import AuditLog
from audit.services import audit_log
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_audit_log_creates_row():
    organization = OrganizationFactory()
    actor = OwnerFactory(organization=organization)
    resource_uuid = uuid.uuid4()

    entry = audit_log(
        organization=organization,
        actor=actor,
        action="MEMBERSHIP_FREEZE",
        resource_type="membership",
        resource_uuid=resource_uuid,
        before={"status": "ACTIVE"},
        after={"status": "FROZEN"},
        request_id="req-1",
        system_initiated=False,
    )

    assert AuditLog.objects.count() == 1
    assert entry.pk is not None
    assert entry.organization == organization
    assert entry.actor == actor
    assert entry.action == "MEMBERSHIP_FREEZE"
    assert entry.resource_type == "membership"
    assert entry.resource_uuid == resource_uuid
    assert entry.before_state == {"status": "ACTIVE"}
    assert entry.after_state == {"status": "FROZEN"}
    assert entry.request_id == "req-1"
    assert entry.system_initiated is False
    assert entry.occurred_at is not None
