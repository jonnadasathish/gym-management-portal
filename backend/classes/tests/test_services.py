from datetime import timedelta

import pytest
from django.utils import timezone

from classes.models import Booking
from classes.services import BookingError, book_occurrence, cancel_booking
from classes.tests.factories import ClassOccurrenceFactory, GymClassFactory
from members.tests.factories import MemberFactory
from pt.services import schedule_session
from pt.tests.factories import PTPackageFactory

pytestmark = pytest.mark.django_db


def test_booking_succeeds_under_capacity():
    occurrence = ClassOccurrenceFactory()
    member = MemberFactory(organization=occurrence.organization, home_branch=occurrence.gym_class.branch)
    booking = book_occurrence(occurrence_id=occurrence.id, member=member)
    assert booking.status == Booking.Status.BOOKED


def test_capacity_cannot_be_exceeded():
    gym_class = GymClassFactory(capacity=1)
    occurrence = ClassOccurrenceFactory(gym_class=gym_class, organization=gym_class.organization)
    m1 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    m2 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    book_occurrence(occurrence_id=occurrence.id, member=m1)
    with pytest.raises(BookingError) as exc:
        book_occurrence(occurrence_id=occurrence.id, member=m2)
    assert exc.value.code == "CLASS_FULL"


def test_waitlist_when_requested_and_full():
    gym_class = GymClassFactory(capacity=1)
    occurrence = ClassOccurrenceFactory(gym_class=gym_class, organization=gym_class.organization)
    m1 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    m2 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    book_occurrence(occurrence_id=occurrence.id, member=m1)
    waitlisted = book_occurrence(occurrence_id=occurrence.id, member=m2, waitlist_if_full=True)
    assert waitlisted.status == Booking.Status.WAITLISTED


def test_member_cannot_book_overlapping_sessions():
    start = timezone.now() + timedelta(hours=3)
    first_class = GymClassFactory()
    second_class = GymClassFactory(
        organization=first_class.organization,
        branch=first_class.branch,
    )
    first = ClassOccurrenceFactory(
        gym_class=first_class,
        organization=first_class.organization,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    second = ClassOccurrenceFactory(
        gym_class=second_class,
        organization=first_class.organization,
        start_time=start + timedelta(minutes=30),
        end_time=start + timedelta(hours=2),
    )
    member = MemberFactory(organization=first_class.organization, home_branch=first_class.branch)
    book_occurrence(occurrence_id=first.id, member=member)
    with pytest.raises(BookingError) as exc:
        book_occurrence(occurrence_id=second.id, member=member)
    assert exc.value.code == "MEMBER_OVERLAP"


def test_class_booking_rejects_trainer_pt_conflict():
    start = timezone.now() + timedelta(days=3)
    gym_class = GymClassFactory()
    package = PTPackageFactory(
        trainer=gym_class.trainer,
        organization=gym_class.organization,
        member__organization=gym_class.organization,
        member__home_branch=gym_class.branch,
    )
    schedule_session(package_id=package.id, scheduled_at=start + timedelta(minutes=15), duration_minutes=60)
    occurrence = ClassOccurrenceFactory(
        gym_class=gym_class,
        organization=gym_class.organization,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    member = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    with pytest.raises(BookingError) as exc:
        book_occurrence(occurrence_id=occurrence.id, member=member)
    assert exc.value.code == "TRAINER_CONFLICT"


def test_cancel_releases_capacity():
    gym_class = GymClassFactory(capacity=1)
    occurrence = ClassOccurrenceFactory(gym_class=gym_class, organization=gym_class.organization)
    m1 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    m2 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    first = book_occurrence(occurrence_id=occurrence.id, member=m1)
    cancel_booking(booking_id=first.id)
    second = book_occurrence(occurrence_id=occurrence.id, member=m2)
    assert second.status == Booking.Status.BOOKED
    assert Booking.objects.filter(occurrence=occurrence, status=Booking.Status.BOOKED).count() == 1


def test_cancel_does_not_auto_promote_waitlist():
    gym_class = GymClassFactory(capacity=1)
    occurrence = ClassOccurrenceFactory(gym_class=gym_class, organization=gym_class.organization)
    m1 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    m2 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    first = book_occurrence(occurrence_id=occurrence.id, member=m1)
    waitlisted = book_occurrence(occurrence_id=occurrence.id, member=m2, waitlist_if_full=True)
    cancel_booking(booking_id=first.id)
    waitlisted.refresh_from_db()
    assert waitlisted.status == Booking.Status.WAITLISTED
