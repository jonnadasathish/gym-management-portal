from decimal import Decimal

import factory

from accounts.tests.factories import UserFactory
from trainers.models import TrainerProfile


class TrainerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TrainerProfile

    user = factory.SubFactory(UserFactory, role="TRAINER")
    organization = factory.SelfAttribute("user.organization")
    specializations = factory.LazyFunction(list)
    certifications = factory.LazyFunction(list)
    compensation_model = TrainerProfile.CompensationModel.FIXED_SALARY
    compensation_rate = Decimal("0.00")
    bio = ""
