"""Staff directory write API (REQ-046): OWNER creates/activates/deactivates staff."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from accounts.tests.factories import OwnerFactory, UserFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from trainers.models import TrainerProfile

pytestmark = pytest.mark.django_db

STAFF_URL = "/api/v1/auth/staff/"


def test_owner_creates_trainer_and_trainer_can_login():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    response = auth_client(owner).post(
        STAFF_URL,
        {
            "email": "trainer.new@example.com",
            "password": "TrainerPass123!",
            "full_name": "New Trainer",
            "phone": "+919876543210",
            "role": "TRAINER",
            "home_branch_id": str(branch.uuid),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    payload = response.data["data"]
    assert payload["role"] == User.Role.TRAINER
    assert payload["email"] == "trainer.new@example.com"
    assert payload["is_active"] is True
    assert payload["trainer_profile"] is not None
    assert payload["trainer_profile"]["specializations"] == []
    assert payload["trainer_profile"]["compensation_model"] == TrainerProfile.CompensationModel.FIXED_SALARY

    created = User.objects.get(email="trainer.new@example.com")
    assert created.organization_id == owner.organization_id
    assert created.check_password("TrainerPass123!")
    assert TrainerProfile.objects.filter(user=created, organization=owner.organization).exists()

    login = APIClient().post(
        "/api/v1/auth/login/",
        {"email": "trainer.new@example.com", "password": "TrainerPass123!"},
    )
    assert login.status_code == status.HTTP_200_OK
    assert login.data["data"]["user"]["role"] == User.Role.TRAINER


def test_staff_admin_cannot_deactivate_staff():
    staff = UserFactory(role=User.Role.STAFF_ADMIN)
    other = UserFactory(organization=staff.organization, role=User.Role.STAFF_ADMIN)
    response = auth_client(staff).post(f"{STAFF_URL}{other.uuid}/deactivate/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    other.refresh_from_db()
    assert other.is_active is True


def test_staff_admin_cannot_create_staff():
    staff = UserFactory(role=User.Role.STAFF_ADMIN)
    response = auth_client(staff).post(
        STAFF_URL,
        {
            "email": "newstaff@example.com",
            "password": "StaffPass123!",
            "full_name": "New Staff",
            "phone": "+919111111111",
            "role": "STAFF_ADMIN",
            "home_branch_id": str(staff.home_branch.uuid),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not User.objects.filter(email="newstaff@example.com").exists()


def test_org_a_cannot_deactivate_org_b_user():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    staff_b = UserFactory(organization=owner_b.organization, role=User.Role.STAFF_ADMIN)
    response = auth_client(owner_a).post(f"{STAFF_URL}{staff_b.uuid}/deactivate/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    staff_b.refresh_from_db()
    assert staff_b.is_active is True


def test_cannot_deactivate_self():
    owner = OwnerFactory()
    response = auth_client(owner).post(f"{STAFF_URL}{owner.uuid}/deactivate/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    owner.refresh_from_db()
    assert owner.is_active is True


def test_cannot_deactivate_owner():
    owner = OwnerFactory()
    other_owner = OwnerFactory(organization=owner.organization, email="coowner@example.com")
    response = auth_client(owner).post(f"{STAFF_URL}{other_owner.uuid}/deactivate/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    other_owner.refresh_from_db()
    assert other_owner.is_active is True


def test_owner_list_includes_inactive_staff():
    owner = OwnerFactory()
    active = UserFactory(organization=owner.organization, role=User.Role.STAFF_ADMIN, full_name="Active Staff")
    inactive = UserFactory(
        organization=owner.organization,
        role=User.Role.STAFF_ADMIN,
        is_active=False,
        full_name="Inactive Staff",
    )
    response = auth_client(owner).get(STAFF_URL)
    assert response.status_code == status.HTTP_200_OK
    ids = {row["id"] for row in response.data["data"]}
    assert str(active.uuid) in ids
    assert str(inactive.uuid) in ids


def test_staff_admin_list_is_active_only():
    owner = OwnerFactory()
    staff = UserFactory(organization=owner.organization, role=User.Role.STAFF_ADMIN, full_name="Front Desk")
    inactive = UserFactory(
        organization=owner.organization,
        role=User.Role.STAFF_ADMIN,
        is_active=False,
        full_name="Former Staff",
    )
    response = auth_client(staff).get(STAFF_URL)
    assert response.status_code == status.HTTP_200_OK
    ids = {row["id"] for row in response.data["data"]}
    assert str(staff.uuid) in ids
    assert str(inactive.uuid) not in ids
