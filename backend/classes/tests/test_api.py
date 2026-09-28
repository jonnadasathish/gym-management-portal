from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from accounts.tests.factories import OwnerFactory, UserFactory
from classes.tests.factories import ClassOccurrenceFactory, GymClassFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from pt.services import schedule_session
from pt.tests.factories import PTPackageFactory

pytestmark = pytest.mark.django_db


def test_owner_books_and_cancels_via_api():
    owner = OwnerFactory()
    occurrence = ClassOccurrenceFactory(
        gym_class__organization=owner.organization,
        gym_class__branch__organization=owner.organization,
        organization=owner.organization,
    )
    member = MemberFactory(organization=owner.organization, home_branch=occurrence.gym_class.branch)
    client = auth_client(owner)
    booked = client.post(
        "/api/v1/classes/bookings/book/",
        {"occurrence_id": str(occurrence.uuid), "member_id": str(member.uuid)},
        format="json",
    )
    assert booked.status_code == status.HTTP_201_CREATED
    booking_id = booked.data["data"]["id"]
    cancelled = client.post(f"/api/v1/classes/bookings/{booking_id}/cancel/")
    assert cancelled.status_code == 200
    assert cancelled.data["data"]["status"] == "CANCELLED"


def test_other_org_cannot_see_occurrence():
    owner_a = OwnerFactory()
    occurrence = ClassOccurrenceFactory()
    response = auth_client(owner_a).get(f"/api/v1/classes/occurrences/{occurrence.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_owner_creates_class_and_occurrence():
    owner = OwnerFactory()
    trainer = UserFactory(role="TRAINER", organization=owner.organization)
    from branches.tests.factories import BranchFactory

    branch = BranchFactory(organization=owner.organization)
    client = auth_client(owner)
    created = client.post(
        "/api/v1/classes/catalog/",
        {"name": "HIIT", "branch_id": str(branch.uuid), "trainer_id": str(trainer.uuid), "capacity": 12},
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED
    start = timezone.now() + timedelta(days=1)
    occurrence = client.post(
        "/api/v1/classes/occurrences/",
        {
            "gym_class_id": created.data["data"]["id"],
            "start_time": start.isoformat(),
            "end_time": (start + timedelta(hours=1)).isoformat(),
        },
        format="json",
    )
    assert occurrence.status_code == status.HTTP_201_CREATED
    assert occurrence.data["data"]["status"] == "SCHEDULED"


def test_occurrence_create_rejects_trainer_conflict():
    owner = OwnerFactory()
    gym_class = GymClassFactory(organization=owner.organization, branch__organization=owner.organization)
    start = timezone.now() + timedelta(days=4)
    package = PTPackageFactory(
        trainer=gym_class.trainer,
        organization=owner.organization,
        member__organization=owner.organization,
        member__home_branch=gym_class.branch,
    )
    schedule_session(package_id=package.id, scheduled_at=start, duration_minutes=60)
    response = auth_client(owner).post(
        "/api/v1/classes/occurrences/",
        {
            "gym_class_id": str(gym_class.uuid),
            "start_time": start.isoformat(),
            "end_time": (start + timedelta(hours=1)).isoformat(),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["error"]["code"] == "TRAINER_CONFLICT"


def test_member_cannot_create_class():
    owner = OwnerFactory()
    member_user = UserFactory(role="MEMBER", organization=owner.organization)
    from branches.tests.factories import BranchFactory

    branch = BranchFactory(organization=owner.organization)
    response = auth_client(member_user).post(
        "/api/v1/classes/catalog/",
        {"name": "Stolen", "branch_id": str(branch.uuid), "capacity": 5},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
