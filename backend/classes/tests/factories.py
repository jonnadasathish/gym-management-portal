from datetime import timedelta

import factory
from django.utils import timezone

from accounts.tests.factories import UserFactory
from branches.tests.factories import BranchFactory
from classes.models import Booking, ClassOccurrence, GymClass
from members.tests.factories import MemberFactory


class GymClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GymClass

    organization = factory.SelfAttribute("branch.organization")
    branch = factory.SubFactory(BranchFactory)
    name = factory.Sequence(lambda n: f"Yoga {n}")
    trainer = factory.SubFactory(UserFactory, role="TRAINER", organization=factory.SelfAttribute("..organization"))
    capacity = 2
    status = GymClass.Status.ACTIVE


class ClassOccurrenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassOccurrence

    gym_class = factory.SubFactory(GymClassFactory)
    organization = factory.SelfAttribute("gym_class.organization")
    start_time = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=2))
    end_time = factory.LazyAttribute(lambda o: o.start_time + timedelta(hours=1))
    status = ClassOccurrence.Status.SCHEDULED


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    occurrence = factory.SubFactory(ClassOccurrenceFactory)
    member = factory.SubFactory(MemberFactory, organization=factory.SelfAttribute("..occurrence.organization"))
    organization = factory.SelfAttribute("occurrence.organization")
    status = Booking.Status.BOOKED
