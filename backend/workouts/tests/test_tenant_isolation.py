import pytest

from organizations.tests.factories import OrganizationFactory
from workouts.models import Exercise, WorkoutProgram
from workouts.tests.factories import ExerciseFactory, WorkoutProgramFactory

pytestmark = pytest.mark.django_db


def test_org_a_cannot_see_org_b_exercise():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    exercise_a = ExerciseFactory(organization=org_a)
    exercise_b = ExerciseFactory(organization=org_b)
    visible = Exercise.objects.for_organization(org_a)
    assert exercise_a in visible
    assert exercise_b not in visible


def test_org_a_cannot_see_org_b_program():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    program_a = WorkoutProgramFactory(member__organization=org_a, organization=org_a)
    program_b = WorkoutProgramFactory(member__organization=org_b, organization=org_b)
    visible = WorkoutProgram.objects.for_organization(org_a)
    assert program_a in visible
    assert program_b not in visible
