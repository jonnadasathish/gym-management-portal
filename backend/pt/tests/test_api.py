import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from core.tests.api import auth_client
from pt.models import PTSession
from pt.tests.factories import PTPackageFactory, PTSessionFactory

pytestmark = pytest.mark.django_db


def test_owner_completes_pt_session_via_api():
    owner = OwnerFactory()
    package = PTPackageFactory(member__organization=owner.organization, organization=owner.organization)
    session = PTSessionFactory(
        package=package, member=package.member, trainer=package.trainer, organization=owner.organization
    )
    response = auth_client(owner).post(f"/api/v1/pt/sessions/{session.uuid}/complete/")
    assert response.status_code == 200
    assert response.data["data"]["status"] == "COMPLETED"


def test_other_org_cannot_see_pt_package():
    owner = OwnerFactory()
    package = PTPackageFactory()
    response = auth_client(owner).get(f"/api/v1/pt/packages/{package.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_owner_creates_package_and_schedules_session():
    from datetime import timedelta

    from django.utils import timezone

    from accounts.tests.factories import UserFactory
    from members.tests.factories import MemberFactory

    owner = OwnerFactory()
    trainer = UserFactory(role="TRAINER", organization=owner.organization)
    member = MemberFactory(organization=owner.organization)
    client = auth_client(owner)
    created = client.post(
        "/api/v1/pt/packages/",
        {
            "member_id": str(member.uuid),
            "trainer_id": str(trainer.uuid),
            "plan_name": "8 sessions",
            "sessions_purchased": 8,
            "price": "12000.00",
        },
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED
    assert created.data["data"]["sessions_remaining"] == 8
    scheduled = client.post(
        "/api/v1/pt/sessions/schedule/",
        {
            "package_id": created.data["data"]["id"],
            "scheduled_at": (timezone.now() + timedelta(days=2)).isoformat(),
            "duration_minutes": 45,
        },
        format="json",
    )
    assert scheduled.status_code == status.HTTP_201_CREATED
    assert scheduled.data["data"]["status"] == "SCHEDULED"


def test_owner_reschedules_pt_session():
    from datetime import timedelta

    from django.utils import timezone

    owner = OwnerFactory()
    package = PTPackageFactory(member__organization=owner.organization, organization=owner.organization)
    session = PTSessionFactory(
        package=package, member=package.member, trainer=package.trainer, organization=owner.organization
    )
    new_start = timezone.now() + timedelta(days=5)
    response = auth_client(owner).post(
        f"/api/v1/pt/sessions/{session.uuid}/reschedule/",
        {"scheduled_at": new_start.isoformat(), "duration_minutes": 30},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["id"] == str(session.uuid)
    assert response.data["data"]["status"] == "SCHEDULED"
    assert response.data["data"]["duration_minutes"] == 30
    session.refresh_from_db()
    assert session.status == "SCHEDULED"
    assert PTSession.objects.filter(package=package).count() == 1


def test_reschedule_api_rejects_overlap():
    from datetime import timedelta

    from django.utils import timezone

    from pt.services import schedule_session

    owner = OwnerFactory()
    package = PTPackageFactory(member__organization=owner.organization, organization=owner.organization)
    start = timezone.now() + timedelta(days=2)
    schedule_session(package_id=package.id, scheduled_at=start, duration_minutes=60)
    later = schedule_session(package_id=package.id, scheduled_at=start + timedelta(hours=3), duration_minutes=60)
    response = auth_client(owner).post(
        f"/api/v1/pt/sessions/{later.uuid}/reschedule/",
        {"scheduled_at": (start + timedelta(minutes=15)).isoformat()},
        format="json",
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["error"]["code"] == "MEMBER_OVERLAP"


def test_cannot_reschedule_completed_via_api():
    owner = OwnerFactory()
    package = PTPackageFactory(member__organization=owner.organization, organization=owner.organization)
    session = PTSessionFactory(
        package=package, member=package.member, trainer=package.trainer, organization=owner.organization
    )
    client = auth_client(owner)
    completed = client.post(f"/api/v1/pt/sessions/{session.uuid}/complete/")
    assert completed.status_code == status.HTTP_200_OK
    from datetime import timedelta

    from django.utils import timezone

    response = client.post(
        f"/api/v1/pt/sessions/{session.uuid}/reschedule/",
        {"scheduled_at": (timezone.now() + timedelta(days=4)).isoformat()},
        format="json",
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["error"]["code"] == "INVALID_STATUS"
