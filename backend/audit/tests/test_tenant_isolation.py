"""Mandatory tenant-isolation coverage for audit.AuditLog (AGENTS.md §16.4)."""

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from audit.models import AuditLog
from audit.services import audit_log
from core.tests.api import auth_client

pytestmark = pytest.mark.django_db


def test_org_a_cannot_list_org_b_logs():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    log_a = audit_log(
        organization=owner_a.organization,
        actor=owner_a,
        action="MEMBERSHIP_FREEZE",
        resource_type="membership",
    )
    log_b = audit_log(
        organization=owner_b.organization,
        actor=owner_b,
        action="PAYMENT_REFUND",
        resource_type="payment",
    )

    visible = AuditLog.objects.for_organization(owner_a.organization)
    assert log_a in visible
    assert log_b not in visible

    response = auth_client(owner_a).get("/api/v1/audit/")
    assert response.status_code == status.HTTP_200_OK
    ids = {row["id"] for row in response.data["data"]}
    assert str(log_a.uuid) in ids
    assert str(log_b.uuid) not in ids
