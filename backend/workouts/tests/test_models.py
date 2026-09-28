import datetime

import pytest
from django.core.exceptions import ValidationError

from accounts.tests.factories import UserFactory
from members.tests.factories import MemberFactory
from workouts.models import WorkoutLog, WorkoutProgram
from workouts.tests.factories import WorkoutDayExerciseFactory, WorkoutLogFactory, WorkoutProgramFactory

pytestmark = pytest.mark.django_db


def test_workout_program_create_happy_path():
    program = WorkoutProgramFactory()
    assert program.status == WorkoutProgram.Status.ACTIVE
    assert program.uuid is not None
    assert program.trainer.role == "TRAINER"


def test_workout_log_create_happy_path():
    log = WorkoutLogFactory()
    assert log.sets == 3
    assert log.reps == 10
    assert log.uuid is not None
    assert log.workout_day_exercise_id is None


def test_program_trainer_must_have_trainer_role():
    member = MemberFactory()
    staff = UserFactory(organization=member.organization, role="STAFF_ADMIN")
    program = WorkoutProgram(
        organization=member.organization,
        member=member,
        trainer=staff,
        name="Invalid trainer",
        start_date=datetime.date.today(),
    )
    with pytest.raises(ValidationError):
        program.full_clean()


def test_log_member_must_match_program_member():
    prescription = WorkoutDayExerciseFactory()
    other_member = MemberFactory(organization=prescription.organization)
    log = WorkoutLog(
        organization=prescription.organization,
        member=other_member,
        workout_day_exercise=prescription,
        exercise=prescription.exercise,
        performed_on=datetime.date.today(),
        sets=3,
        reps=10,
    )
    with pytest.raises(ValidationError):
        log.full_clean()
