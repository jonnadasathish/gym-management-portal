import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory, UserFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from notifications.models import NotificationChannel, NotificationEventType
from notifications.tests.factories import NotificationLogFactory

pytestmark = pytest.mark.django_db


def test_owner_lists_org_logs():
    owner = OwnerFactory()
    own = NotificationLogFactory(organization=owner.organization)
    NotificationLogFactory()
    response = auth_client(owner).get("/api/v1/notifications/logs/")
    assert response.status_code == 200
    ids = {row["id"] for row in response.data["data"]}
    assert str(own.uuid) in ids
    assert len(ids) == 1


def test_member_sees_only_own_logs():
    owner = OwnerFactory()
    member_user = UserFactory(role="MEMBER", organization=owner.organization)
    member = MemberFactory(organization=owner.organization, user=member_user)
    own = NotificationLogFactory(
        organization=owner.organization,
        recipient_member=member,
        recipient_user=member_user,
    )
    NotificationLogFactory(organization=owner.organization)
    response = auth_client(member_user).get("/api/v1/notifications/logs/")
    assert response.status_code == 200
    ids = {row["id"] for row in response.data["data"]}
    assert ids == {str(own.uuid)}


def test_other_org_cannot_see_log():
    owner = OwnerFactory()
    other = NotificationLogFactory()
    response = auth_client(owner).get(f"/api/v1/notifications/logs/{other.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_front_desk_can_create_template():
    owner = OwnerFactory()
    response = auth_client(owner).post(
        "/api/v1/notifications/templates/",
        {
            "event_type": NotificationEventType.CLASS_BOOKING,
            "channel": NotificationChannel.IN_APP,
            "body": "CLASS_BOOKING",
            "is_active": True,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data["data"]["event_type"] == NotificationEventType.CLASS_BOOKING


def test_member_cannot_create_template():
    owner = OwnerFactory()
    member_user = UserFactory(role="MEMBER", organization=owner.organization)
    response = auth_client(member_user).post(
        "/api/v1/notifications/templates/",
        {
            "event_type": NotificationEventType.BIRTHDAY,
            "channel": NotificationChannel.IN_APP,
            "body": "BIRTHDAY",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_front_desk_emit_enqueues_sent_log():
    owner = OwnerFactory()
    member = MemberFactory(organization=owner.organization)
    response = auth_client(owner).post(
        "/api/v1/notifications/emit/",
        {
            "event_type": NotificationEventType.FREEZE_APPROVED,
            "member_id": str(member.uuid),
            "channel": NotificationChannel.IN_APP,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data["data"]["status"] == "SENT"
    assert response.data["data"]["event_type"] == NotificationEventType.FREEZE_APPROVED
