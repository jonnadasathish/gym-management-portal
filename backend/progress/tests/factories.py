from datetime import date
from decimal import Decimal

import factory
from django.utils import timezone

from members.tests.factories import MemberFactory
from progress.models import PersonalBest, ProgressEntry


class ProgressEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProgressEntry

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    recorded_at = factory.LazyFunction(timezone.now)
    weight_kg = Decimal("70.00")
    height_cm = None
    body_fat_pct = None
    measurements = factory.LazyFunction(dict)
    photo_url = ""
    notes = ""


class PersonalBestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PersonalBest

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    exercise_name = "Bench press"
    value = Decimal("80.00")
    unit = "kg"
    achieved_at = factory.LazyFunction(date.today)
