import datetime

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory, UserFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from workouts.tests.factories import WorkoutProgramFactory

pytestmark = pytest.mark.django_db


def test_owner_creates_program_with_day_and_exercise_member_isolation_404():
    owner = OwnerFactory()
    trainer = UserFactory(role="TRAINER", organization=owner.organization)
    member = MemberFactory(organization=owner.organization)
    client = auth_client(owner)

    exercise = client.post(
        "/api/v1/workouts/exercises/",
        {"name": "Back Squat", "muscle_group": "legs", "equipment": "barbell"},
        format="json",
    )
    assert exercise.status_code == status.HTTP_201_CREATED
    exercise_id = exercise.data["data"]["id"]

    created = client.post(
        "/api/v1/workouts/programs/",
        {
            "member_id": str(member.uuid),
            "trainer_id": str(trainer.uuid),
            "name": "Beginner Strength",
            "start_date": datetime.date.today().isoformat(),
            "days": [
                {
                    "label": "Day 1",
                    "day_index": 1,
                    "exercises": [
                        {
                            "exercise_id": exercise_id,
                            "target_sets": 3,
                            "target_reps": 8,
                            "order": 1,
                        }
                    ],
                }
            ],
        },
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED
    payload = created.data["data"]
    assert payload["name"] == "Beginner Strength"
    assert payload["days"][0]["label"] == "Day 1"
    assert payload["days"][0]["exercises"][0]["target_sets"] == 3
    assert payload["days"][0]["exercises"][0]["exercise_id"] == exercise_id

    other_user = UserFactory(role="MEMBER", organization=owner.organization)
    MemberFactory(organization=owner.organization, user=other_user, home_branch=member.home_branch)
    isolated = auth_client(other_user).get(f"/api/v1/workouts/programs/{payload['id']}/")
    assert isolated.status_code == status.HTTP_404_NOT_FOUND


def test_other_org_cannot_see_program():
    owner = OwnerFactory()
    program = WorkoutProgramFactory()
    response = auth_client(owner).get(f"/api/v1/workouts/programs/{program.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
