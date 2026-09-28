from datetime import date, timedelta

import pytest
from django.utils import timezone

from classes.models import Booking, ClassOccurrence
from classes.tests.factories import BookingFactory, ClassOccurrenceFactory
from members.tests.factories import MemberFactory
from memberships.models import Membership
from memberships.tests.factories import MembershipFactory
from notifications.models import NotificationChannel, NotificationEventType, NotificationLog
from notifications.services import (
    emit_birthday_reminders,
    emit_class_reminders,
    emit_membership_expired_reminders,
    emit_membership_expiring_reminders,
    emit_pt_reminders,
)
from organizations.tests.factories import OrganizationFactory
from pt.models import PTSession
from pt.tests.factories import PTSessionFactory

pytestmark = pytest.mark.django_db


def test_expiring_membership_in_three_days_notifies_once():
    as_of = timezone.now()
    membership = MembershipFactory(
        status=Membership.Status.ACTIVE,
        start_date=as_of.date() - timedelta(days=27),
        end_date=as_of.date() + timedelta(days=3),
    )

    emit_membership_expiring_reminders(as_of=as_of, days=7)
    logs = NotificationLog.objects.filter(event_type=NotificationEventType.MEMBERSHIP_EXPIRING)
    assert logs.count() == 1
    log = logs.get()
    assert log.organization_id == membership.organization_id
    assert log.recipient_member_id == membership.member_id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["membership_id"] == str(membership.uuid)
    assert log.payload["end_date"] == membership.end_date.isoformat()

    emit_membership_expiring_reminders(as_of=as_of, days=7)
    assert NotificationLog.objects.filter(event_type=NotificationEventType.MEMBERSHIP_EXPIRING).count() == 1


def test_membership_ending_in_30_days_does_not_notify_at_days_7():
    as_of = timezone.now()
    MembershipFactory(
        status=Membership.Status.ACTIVE,
        start_date=as_of.date(),
        end_date=as_of.date() + timedelta(days=30),
    )

    emit_membership_expiring_reminders(as_of=as_of, days=7)
    assert not NotificationLog.objects.filter(event_type=NotificationEventType.MEMBERSHIP_EXPIRING).exists()


def test_booked_class_in_two_hours_notifies_waitlisted_does_not():
    as_of = timezone.now()
    start_time = as_of + timedelta(hours=2)
    occurrence = ClassOccurrenceFactory(
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        status=ClassOccurrence.Status.SCHEDULED,
    )
    booked = BookingFactory(
        occurrence=occurrence,
        organization=occurrence.organization,
        member=MemberFactory(organization=occurrence.organization, home_branch=occurrence.gym_class.branch),
        status=Booking.Status.BOOKED,
    )
    waitlisted = BookingFactory(
        occurrence=occurrence,
        organization=occurrence.organization,
        member=MemberFactory(organization=occurrence.organization, home_branch=occurrence.gym_class.branch),
        status=Booking.Status.WAITLISTED,
    )

    emit_class_reminders(as_of=as_of, hours=24)
    logs = NotificationLog.objects.filter(event_type=NotificationEventType.CLASS_REMINDER)
    assert logs.count() == 1
    log = logs.get()
    assert log.recipient_member_id == booked.member_id
    assert log.recipient_member_id != waitlisted.member_id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["booking_id"] == str(booked.uuid)
    assert log.payload["occurrence_id"] == str(occurrence.uuid)
    assert log.payload["start_time"] == occurrence.start_time.isoformat()


def test_scheduled_pt_in_two_hours_notifies_completed_does_not():
    as_of = timezone.now()
    scheduled_at = as_of + timedelta(hours=2)
    scheduled = PTSessionFactory(scheduled_at=scheduled_at, status=PTSession.Status.SCHEDULED)
    completed = PTSessionFactory(scheduled_at=scheduled_at, status=PTSession.Status.COMPLETED)

    emit_pt_reminders(as_of=as_of, hours=24)
    logs = NotificationLog.objects.filter(event_type=NotificationEventType.PT_REMINDER)
    assert logs.count() == 1
    log = logs.get()
    assert log.recipient_member_id == scheduled.member_id
    assert log.recipient_member_id != completed.member_id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["session_id"] == str(scheduled.uuid)
    assert log.payload["scheduled_at"] == scheduled.scheduled_at.isoformat()


def test_org_b_membership_does_not_create_org_a_log():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    as_of = timezone.now()
    membership_b = MembershipFactory(
        member=MemberFactory(organization=org_b),
        organization=org_b,
        status=Membership.Status.ACTIVE,
        start_date=as_of.date() - timedelta(days=27),
        end_date=as_of.date() + timedelta(days=3),
    )

    emit_membership_expiring_reminders(as_of=as_of, days=7)

    assert not NotificationLog.objects.for_organization(org_a).exists()
    log = NotificationLog.objects.for_organization(org_b).get(
        event_type=NotificationEventType.MEMBERSHIP_EXPIRING
    )
    assert log.recipient_member_id == membership_b.member_id
    assert log.payload["membership_id"] == str(membership_b.uuid)


def test_overdue_active_membership_expires_and_notifies_once():
    as_of = timezone.now()
    membership = MembershipFactory(
        status=Membership.Status.ACTIVE,
        start_date=as_of.date() - timedelta(days=31),
        end_date=as_of.date() - timedelta(days=1),
    )

    emit_membership_expired_reminders(as_of=as_of)
    membership.refresh_from_db()
    assert membership.status == Membership.Status.EXPIRED
    logs = NotificationLog.objects.filter(event_type=NotificationEventType.MEMBERSHIP_EXPIRED)
    assert logs.count() == 1
    log = logs.get()
    assert log.organization_id == membership.organization_id
    assert log.recipient_member_id == membership.member_id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["membership_id"] == str(membership.uuid)
    assert log.payload["end_date"] == membership.end_date.isoformat()

    emit_membership_expired_reminders(as_of=as_of)
    membership.refresh_from_db()
    assert membership.status == Membership.Status.EXPIRED
    assert NotificationLog.objects.filter(event_type=NotificationEventType.MEMBERSHIP_EXPIRED).count() == 1


def test_frozen_overdue_membership_is_not_expired_or_notified():
    as_of = timezone.now()
    membership = MembershipFactory(
        status=Membership.Status.FROZEN,
        start_date=as_of.date() - timedelta(days=31),
        end_date=as_of.date() - timedelta(days=1),
    )

    emit_membership_expired_reminders(as_of=as_of)
    membership.refresh_from_db()
    assert membership.status == Membership.Status.FROZEN
    assert not NotificationLog.objects.filter(event_type=NotificationEventType.MEMBERSHIP_EXPIRED).exists()


def test_birthday_today_notifies_once_other_dob_does_not():
    as_of = timezone.now()
    today = as_of.date()
    birthday_member = MemberFactory(dob=date(1992, today.month, today.day))
    other_month = 1 if today.month != 1 else 2
    other_member = MemberFactory(dob=date(1992, other_month, 15))

    emit_birthday_reminders(as_of=as_of)
    logs = NotificationLog.objects.filter(event_type=NotificationEventType.BIRTHDAY)
    assert logs.count() == 1
    log = logs.get()
    assert log.recipient_member_id == birthday_member.id
    assert log.recipient_member_id != other_member.id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["birthday_on"] == today.isoformat()

    emit_birthday_reminders(as_of=as_of)
    assert NotificationLog.objects.filter(event_type=NotificationEventType.BIRTHDAY).count() == 1


def test_member_without_dob_does_not_notify_birthday():
    as_of = timezone.now()
    MemberFactory(dob=None)

    emit_birthday_reminders(as_of=as_of)
    assert not NotificationLog.objects.filter(event_type=NotificationEventType.BIRTHDAY).exists()


def test_org_b_birthday_does_not_create_org_a_log():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    as_of = timezone.now()
    today = as_of.date()
    member_b = MemberFactory(organization=org_b, dob=date(1992, today.month, today.day))

    emit_birthday_reminders(as_of=as_of)

    assert not NotificationLog.objects.for_organization(org_a).exists()
    log = NotificationLog.objects.for_organization(org_b).get(event_type=NotificationEventType.BIRTHDAY)
    assert log.recipient_member_id == member_b.id
    assert log.payload["birthday_on"] == today.isoformat()
