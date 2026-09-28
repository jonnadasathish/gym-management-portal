from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from pt.models import PTSession
from pt.tests.factories import PTPackageFactory, PTSessionFactory
from trainers.models import TrainerProfile
from trainers.services import calculate_compensation
from trainers.tests.factories import TrainerProfileFactory

pytestmark = pytest.mark.django_db


def test_per_session_compensation_two_completed_sessions():
    profile = TrainerProfileFactory(
        compensation_model=TrainerProfile.CompensationModel.PER_SESSION,
        compensation_rate=Decimal("500.00"),
    )
    trainer = profile.user
    package = PTPackageFactory(
        trainer=trainer,
        organization=trainer.organization,
        member__organization=trainer.organization,
    )
    when = timezone.now()
    day = timezone.localdate()
    PTSessionFactory(
        package=package,
        trainer=trainer,
        member=package.member,
        organization=trainer.organization,
        status=PTSession.Status.COMPLETED,
        scheduled_at=when,
    )
    PTSessionFactory(
        package=package,
        trainer=trainer,
        member=package.member,
        organization=trainer.organization,
        status=PTSession.Status.COMPLETED,
        scheduled_at=when,
    )
    PTSessionFactory(
        package=package,
        trainer=trainer,
        member=package.member,
        organization=trainer.organization,
        status=PTSession.Status.SCHEDULED,
        scheduled_at=when,
    )
    PTSessionFactory(
        package=package,
        trainer=trainer,
        member=package.member,
        organization=trainer.organization,
        status=PTSession.Status.COMPLETED,
        scheduled_at=when - timedelta(days=40),
    )
    result = calculate_compensation(
        trainer_user=trainer,
        start_date=day,
        end_date=day,
    )
    assert result["completed_sessions"] == 2
    assert result["computed_amount"] == Decimal("1000.00")
    assert result["compensation_rate"] == Decimal("500.00")


def test_per_class_compensation_excludes_cancelled_occurrences():
    from classes.models import ClassOccurrence
    from classes.tests.factories import ClassOccurrenceFactory, GymClassFactory

    profile = TrainerProfileFactory(
        compensation_model=TrainerProfile.CompensationModel.PER_CLASS,
        compensation_rate=Decimal("200.00"),
    )
    trainer = profile.user
    gym_class = GymClassFactory(
        trainer=trainer,
        organization=trainer.organization,
        branch__organization=trainer.organization,
    )
    when = timezone.now()
    day = timezone.localdate()
    ClassOccurrenceFactory(
        gym_class=gym_class,
        organization=trainer.organization,
        start_time=when,
        status=ClassOccurrence.Status.SCHEDULED,
    )
    ClassOccurrenceFactory(
        gym_class=gym_class,
        organization=trainer.organization,
        start_time=when,
        status=ClassOccurrence.Status.CANCELLED,
    )
    result = calculate_compensation(
        trainer_user=trainer,
        start_date=day,
        end_date=day,
    )
    assert result["classes_taught"] == 1
    assert result["computed_amount"] == Decimal("200.00")


def test_revenue_share_returns_computed_amount_none():
    profile = TrainerProfileFactory(
        compensation_model=TrainerProfile.CompensationModel.REVENUE_SHARE,
        compensation_rate=Decimal("10.00"),
    )
    day = timezone.localdate()
    result = calculate_compensation(
        trainer_user=profile.user,
        start_date=day,
        end_date=day,
    )
    assert result["computed_amount"] is None
    assert result["completed_sessions"] == 0
    assert result["classes_taught"] == 0
    assert result["compensation_rate"] == Decimal("10.00")
    assert "undefined" in result["note"].lower()
