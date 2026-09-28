"""PT package/session logic (AGENTS.md §24, DEC-020, REQ-042..045).

A completed session decrements the package balance exactly once, under
`select_for_update()` on the package row. Cancelled sessions do not
decrement (REQ-045 default; gym-policy override is not defined — OQ).
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from classes.models import Booking, ClassOccurrence
from pt.models import PTPackage, PTSession


class PTStateError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def _session_end(session):
    return session.scheduled_at + timedelta(minutes=session.duration_minutes)


def member_has_overlapping_hold(*, member, start_time, end_time, exclude_booking_id=None, exclude_session_id=None):
    class_qs = Booking.objects.filter(
        member=member,
        status=Booking.Status.BOOKED,
        occurrence__status=ClassOccurrence.Status.SCHEDULED,
        occurrence__start_time__lt=end_time,
        occurrence__end_time__gt=start_time,
    )
    if exclude_booking_id:
        class_qs = class_qs.exclude(pk=exclude_booking_id)
    if class_qs.exists():
        return True

    sessions = PTSession.objects.filter(member=member, status=PTSession.Status.SCHEDULED)
    if exclude_session_id:
        sessions = sessions.exclude(pk=exclude_session_id)
    for session in sessions:
        if session.scheduled_at < end_time and _session_end(session) > start_time:
            return True
    return False


def trainer_has_overlapping_hold(*, trainer_id, start_time, end_time, exclude_occurrence_id=None, exclude_session_id=None):
    if not trainer_id:
        return False
    occ_qs = ClassOccurrence.objects.filter(
        gym_class__trainer_id=trainer_id,
        status=ClassOccurrence.Status.SCHEDULED,
        start_time__lt=end_time,
        end_time__gt=start_time,
    )
    if exclude_occurrence_id:
        occ_qs = occ_qs.exclude(pk=exclude_occurrence_id)
    if occ_qs.exists():
        return True

    sessions = PTSession.objects.filter(trainer_id=trainer_id, status=PTSession.Status.SCHEDULED)
    if exclude_session_id:
        sessions = sessions.exclude(pk=exclude_session_id)
    for session in sessions:
        if session.scheduled_at < end_time and _session_end(session) > start_time:
            return True
    return False


@transaction.atomic
def schedule_session(*, package_id, scheduled_at, duration_minutes=60, notes=""):
    package = PTPackage.objects.select_for_update().select_related("member", "trainer", "organization").get(pk=package_id)
    if package.sessions_remaining <= 0:
        raise PTStateError("NO_SESSIONS_REMAINING", "This PT package has no remaining sessions.")
    if package.expiry_date and scheduled_at.date() > package.expiry_date:
        raise PTStateError("PACKAGE_EXPIRED", "This PT package has expired.")

    end_time = scheduled_at + timedelta(minutes=duration_minutes)
    if member_has_overlapping_hold(member=package.member, start_time=scheduled_at, end_time=end_time):
        raise PTStateError("MEMBER_OVERLAP", "This member already has an overlapping session.")
    if trainer_has_overlapping_hold(trainer_id=package.trainer_id, start_time=scheduled_at, end_time=end_time):
        raise PTStateError("TRAINER_CONFLICT", "The trainer has a conflicting session at this time.")

    session = PTSession(
        organization=package.organization,
        package=package,
        member=package.member,
        trainer=package.trainer,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
        notes=notes,
        status=PTSession.Status.SCHEDULED,
    )
    session.full_clean()
    session.save()
    _enqueue_pt_booking_notification(session)
    return session


def _enqueue_pt_booking_notification(session):
    """PT_BOOKING is recorded after commit so notify failure cannot undo the session."""

    def _notify():
        try:
            from notifications.models import NotificationChannel, NotificationEventType
            from notifications.services import enqueue_notification

            enqueue_notification(
                organization=session.organization,
                member=session.member,
                event_type=NotificationEventType.PT_BOOKING,
                channel=NotificationChannel.IN_APP,
                context={"session_id": str(session.uuid)},
            )
        except Exception:
            pass

    transaction.on_commit(_notify)


@transaction.atomic
def complete_session(*, session_id):
    session = PTSession.objects.select_for_update().select_related("package").get(pk=session_id)
    if session.status != PTSession.Status.SCHEDULED:
        raise PTStateError("INVALID_STATUS", f"Cannot complete a session in status {session.status!r}.")

    package = PTPackage.objects.select_for_update().get(pk=session.package_id)
    if package.sessions_consumed >= package.sessions_purchased:
        raise PTStateError("NO_SESSIONS_REMAINING", "This PT package has no remaining sessions.")

    package.sessions_consumed += 1
    package.save(update_fields=["sessions_consumed", "updated_at"])
    session.status = PTSession.Status.COMPLETED
    session.save(update_fields=["status", "updated_at"])
    return session, package


@transaction.atomic
def reschedule_session(*, session_id, scheduled_at, duration_minutes=None):
    """In-place reschedule: keep the same row and status SCHEDULED (REQ-043).

    Does not create a second session and does not set status=RESCHEDULED.
    """
    session = PTSession.objects.select_for_update().select_related("member").get(pk=session_id)
    if session.status != PTSession.Status.SCHEDULED:
        raise PTStateError("INVALID_STATUS", f"Cannot reschedule a session in status {session.status!r}.")

    duration = duration_minutes if duration_minutes is not None else session.duration_minutes
    end_time = scheduled_at + timedelta(minutes=duration)
    if member_has_overlapping_hold(
        member=session.member,
        start_time=scheduled_at,
        end_time=end_time,
        exclude_session_id=session.id,
    ):
        raise PTStateError("MEMBER_OVERLAP", "This member already has an overlapping session.")
    if trainer_has_overlapping_hold(
        trainer_id=session.trainer_id,
        start_time=scheduled_at,
        end_time=end_time,
        exclude_session_id=session.id,
    ):
        raise PTStateError("TRAINER_CONFLICT", "The trainer has a conflicting session at this time.")

    session.scheduled_at = scheduled_at
    session.status = PTSession.Status.SCHEDULED
    update_fields = ["scheduled_at", "status", "updated_at"]
    if duration_minutes is not None:
        session.duration_minutes = duration_minutes
        update_fields.insert(1, "duration_minutes")
    session.save(update_fields=update_fields)
    return session


@transaction.atomic
def cancel_session(*, session_id):
    """Cancel does not consume a package session (REQ-045 default)."""
    session = PTSession.objects.select_for_update().get(pk=session_id)
    if session.status != PTSession.Status.SCHEDULED:
        raise PTStateError("INVALID_STATUS", f"Cannot cancel a session in status {session.status!r}.")
    session.status = PTSession.Status.CANCELLED
    session.save(update_fields=["status", "updated_at"])
    return session


@transaction.atomic
def mark_no_show(*, session_id):
    """No-show does not consume a package session (same default as cancel)."""
    session = PTSession.objects.select_for_update().get(pk=session_id)
    if session.status != PTSession.Status.SCHEDULED:
        raise PTStateError("INVALID_STATUS", f"Cannot mark no-show in status {session.status!r}.")
    session.status = PTSession.Status.NO_SHOW
    session.save(update_fields=["status", "updated_at"])
    return session
