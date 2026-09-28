import pytest
from rest_framework import status

from accounts.tests.factories import UserFactory
from core.tests.api import auth_client

pytestmark = pytest.mark.django_db


def test_non_owner_cannot_list_audit_logs():
    staff = UserFactory()
    response = auth_client(staff).get("/api/v1/audit/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert staff.role != "OWNER"
