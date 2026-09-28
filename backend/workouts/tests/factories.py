import datetime
from decimal import Decimal

import factory

from accounts.tests.factories import UserFactory
from members.tests.factories import MemberFactory
from organizations.tests.factories import OrganizationFactory
from workouts.models import Exercise, WorkoutDay, WorkoutDayExercise, WorkoutLog, WorkoutProgram


class ExerciseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Exercise

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Sequence(lambda n: f"Exercise {n}")
    muscle_group = "legs"
    equipment = "barbell"


class WorkoutProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkoutProgram

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    trainer = factory.SubFactory(UserFactory, role="TRAINER", organization=factory.SelfAttribute("..organization"))
    name = "Beginner Strength"
    start_date = factory.LazyFunction(datetime.date.today)
    status = WorkoutProgram.Status.ACTIVE


class WorkoutDayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkoutDay

    program = factory.SubFactory(WorkoutProgramFactory)
    organization = factory.SelfAttribute("program.organization")
    day_index = factory.Sequence(lambda n: n)
    label = factory.Sequence(lambda n: f"Day {n}")


class WorkoutDayExerciseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkoutDayExercise

    workout_day = factory.SubFactory(WorkoutDayFactory)
    organization = factory.SelfAttribute("workout_day.organization")
    exercise = factory.SubFactory(ExerciseFactory, organization=factory.SelfAttribute("..organization"))
    target_sets = 3
    target_reps = 10
    target_weight = Decimal("60.00")
    rest_seconds = 90
    order = 1


class WorkoutLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkoutLog

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    exercise = factory.SubFactory(ExerciseFactory, organization=factory.SelfAttribute("..organization"))
    performed_on = factory.LazyFunction(datetime.date.today)
    sets = 3
    reps = 10
    weight = Decimal("60.00")
