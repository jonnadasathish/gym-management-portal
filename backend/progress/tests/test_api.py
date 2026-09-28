from decimal import Decimal

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from progress.tests.factories import PersonalBestFactory, ProgressEntryFactory

pytestmark = pytest.mark.django_db


def test_owner_creates_progress_entry():
    owner = OwnerFactory()
    member = MemberFactory(organization=owner.organization)
    response = auth_client(owner).post(
        "/api/v1/progress/entries/",
        {
            "member_id": str(member.uuid),
            "weight_kg": "72.50",
            "measurements": {"chest": 98, "waist": 81},
            "notes": "Week 4 check-in",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["data"]["member_id"] == str(member.uuid)
    assert Decimal(str(response.data["data"]["weight_kg"])) == Decimal("72.50")
    assert response.data["data"]["bmi"] is None
    assert response.data["data"]["measurements"]["chest"] == 98


def test_other_org_cannot_see_progress_entry():
    owner = OwnerFactory()
    entry = ProgressEntryFactory()
    response = auth_client(owner).get(f"/api/v1/progress/entries/{entry.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_create_progress_entry_for_other_org_member():
    owner = OwnerFactory()
    other = MemberFactory()
    response = auth_client(owner).post(
        "/api/v1/progress/entries/",
        {"member_id": str(other.uuid), "weight_kg": "70.00"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_bmi_computed_when_weight_and_height_present():
    owner = OwnerFactory()
    member = MemberFactory(organization=owner.organization)
    response = auth_client(owner).post(
        "/api/v1/progress/entries/",
        {
            "member_id": str(member.uuid),
            "weight_kg": "70.00",
            "height_cm": "175.00",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    # BMI = 70 / (1.75^2) = 22.857...
    assert Decimal(str(response.data["data"]["bmi"])) == Decimal("22.86")


def test_owner_creates_personal_best():
    owner = OwnerFactory()
    member = MemberFactory(organization=owner.organization)
    response = auth_client(owner).post(
        "/api/v1/progress/personal-bests/",
        {
            "member_id": str(member.uuid),
            "exercise_name": "Squat",
            "value": "120.00",
            "unit": "kg",
            "achieved_at": "2026-09-28",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["data"]["exercise_name"] == "Squat"
    assert Decimal(str(response.data["data"]["value"])) == Decimal("120.00")


def test_other_org_cannot_see_personal_best():
    owner = OwnerFactory()
    record = PersonalBestFactory()
    response = auth_client(owner).get(f"/api/v1/progress/personal-bests/{record.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
