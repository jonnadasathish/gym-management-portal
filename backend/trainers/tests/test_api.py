from datetime import timedelta
from decimal import Decimal

import pytest
from rest_framework import status

from accounts.models import User
from accounts.tests.factories import OwnerFactory, UserFactory
from core.tests.api import auth_client
from trainers.models import TrainerProfile
from trainers.tests.factories import TrainerProfileFactory

pytestmark = pytest.mark.django_db


def test_owner_lists_org_trainers():
    owner = OwnerFactory()
    mine = TrainerProfileFactory(user__organization=owner.organization, organization=owner.organization)
    TrainerProfileFactory()
    response = auth_client(owner).get("/api/v1/trainers/")
    assert response.status_code == status.HTTP_200_OK
    ids = {row["id"] for row in response.data["data"]}
    assert str(mine.uuid) in ids
    assert len(ids) == 1


def test_trainer_list_is_self_only():
    owner = OwnerFactory()
    self_profile = TrainerProfileFactory(user__organization=owner.organization, organization=owner.organization)
    other = TrainerProfileFactory(user__organization=owner.organization, organization=owner.organization)
    response = auth_client(self_profile.user).get("/api/v1/trainers/")
    assert response.status_code == status.HTTP_200_OK
    ids = {row["id"] for row in response.data["data"]}
    assert ids == {str(self_profile.uuid)}
    assert str(other.uuid) not in ids


def test_staff_admin_cannot_patch_trainer_profile():
    owner = OwnerFactory()
    profile = TrainerProfileFactory(user__organization=owner.organization, organization=owner.organization)
    staff = UserFactory(organization=owner.organization, role=User.Role.STAFF_ADMIN)
    response = auth_client(staff).patch(
        f"/api/v1/trainers/{profile.uuid}/",
        {"bio": "should not land"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_trainer_can_edit_own_extras_but_not_compensation():
    profile = TrainerProfileFactory(
        compensation_model=TrainerProfile.CompensationModel.PER_SESSION,
        compensation_rate=Decimal("500.00"),
    )
    client = auth_client(profile.user)
    ok = client.patch(
        f"/api/v1/trainers/{profile.uuid}/",
        {"bio": "HIIT coach", "specializations": ["HIIT"], "certifications": ["ACE"]},
        format="json",
    )
    assert ok.status_code == status.HTTP_200_OK, ok.data
    assert ok.data["data"]["bio"] == "HIIT coach"
    assert ok.data["data"]["specializations"] == ["HIIT"]

    denied = client.patch(
        f"/api/v1/trainers/{profile.uuid}/",
        {"compensation_rate": "999.00"},
        format="json",
    )
    assert denied.status_code == status.HTTP_403_FORBIDDEN
    profile.refresh_from_db()
    assert profile.compensation_rate == Decimal("500.00")


def test_owner_can_change_compensation():
    owner = OwnerFactory()
    profile = TrainerProfileFactory(user__organization=owner.organization, organization=owner.organization)
    response = auth_client(owner).patch(
        f"/api/v1/trainers/{profile.uuid}/",
        {"compensation_model": "PER_SESSION", "compensation_rate": "500.00"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    profile.refresh_from_db()
    assert profile.compensation_model == TrainerProfile.CompensationModel.PER_SESSION
    assert profile.compensation_rate == Decimal("500.00")


def test_owner_compensation_endpoint_per_session():
    from django.utils import timezone

    from pt.models import PTSession
    from pt.tests.factories import PTPackageFactory, PTSessionFactory

    owner = OwnerFactory()
    profile = TrainerProfileFactory(
        user__organization=owner.organization,
        organization=owner.organization,
        compensation_model=TrainerProfile.CompensationModel.PER_SESSION,
        compensation_rate=Decimal("500.00"),
    )
    trainer = profile.user
    package = PTPackageFactory(
        trainer=trainer,
        organization=owner.organization,
        member__organization=owner.organization,
    )
    when = timezone.now()
    day = timezone.localdate()
    PTSessionFactory(
        package=package,
        trainer=trainer,
        member=package.member,
        organization=owner.organization,
        status=PTSession.Status.COMPLETED,
        scheduled_at=when,
    )
    PTSessionFactory(
        package=package,
        trainer=trainer,
        member=package.member,
        organization=owner.organization,
        status=PTSession.Status.COMPLETED,
        scheduled_at=when,
    )
    start = (day - timedelta(days=1)).isoformat()
    end = (day + timedelta(days=1)).isoformat()
    response = auth_client(owner).get(f"/api/v1/trainers/{profile.uuid}/compensation/?start={start}&end={end}")
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data["data"]["completed_sessions"] == 2
    assert response.data["data"]["computed_amount"] == "1000.00"


def test_staff_admin_cannot_get_compensation():
    owner = OwnerFactory()
    profile = TrainerProfileFactory(user__organization=owner.organization, organization=owner.organization)
    staff = UserFactory(organization=owner.organization, role=User.Role.STAFF_ADMIN)
    response = auth_client(staff).get(
        f"/api/v1/trainers/{profile.uuid}/compensation/?start=2026-09-01&end=2026-09-30"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_member_cannot_list_trainers():
    member = UserFactory(role=User.Role.MEMBER)
    response = auth_client(member).get("/api/v1/trainers/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
