"""Class booking business logic (AGENTS.md §23, DEC-020).

Capacity is decided under `select_for_update()` on the occurrence row so
concurrent bookings cannot exceed `effective_capacity`.

Waitlist auto-promotion is intentionally absent (AGENTS.md §23.4).
"""

from django.db import transaction
from django.utils import timezone

from classes.models import Booking, ClassOccurrence
from pt.services import member_has_overlapping_hold, trainer_has_overlapping_hold


class BookingError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


ACTIVE_HOLD_STATUSES = (Booking.Status.BOOKED, Booking.Status.WAITLISTED)


@transaction.atomic
def book_occurrence(*, occurrence_id, member, waitlist_if_full=False):
    occurrence = (
        ClassOccurrence.objects.select_for_update()
        .select_related("gym_class", "organization")
        .get(pk=occurrence_id)
    )
    if occurrence.status != ClassOccurrence.Status.SCHEDULED:
        raise BookingError("OCCURRENCE_NOT_BOOKABLE", "This class session is not available for booking.")
    if member.organization_id != occurrence.organization_id:
        raise BookingError("TENANT_MISMATCH", "Member and class belong to different organizations.")

    existing = Booking.objects.filter(
        occurrence=occurrence, member=member, status__in=ACTIVE_HOLD_STATUSES
    ).first()
    if existing:
        raise BookingError("ALREADY_BOOKED", "This member already has a booking for this session.")

    if member_has_overlapping_hold(member=member, start_time=occurrence.start_time, end_time=occurrence.end_time):
        raise BookingError("MEMBER_OVERLAP", "This member already has an overlapping booked session.")

    if trainer_has_overlapping_hold(
        trainer_id=occurrence.gym_class.trainer_id,
        start_time=occurrence.start_time,
        end_time=occurrence.end_time,
        exclude_occurrence_id=occurrence.id,
    ):
        raise BookingError("TRAINER_CONFLICT", "The trainer has a conflicting session at this time.")

    booked_count = Booking.objects.filter(occurrence=occurrence, status=Booking.Status.BOOKED).count()
    if booked_count < occurrence.effective_capacity:
        status = Booking.Status.BOOKED
    elif waitlist_if_full:
        status = Booking.Status.WAITLISTED
    else:
        raise BookingError("CLASS_FULL", "This class session is at capacity.")

    booking = Booking(
        organization=occurrence.organization,
        occurrence=occurrence,
        member=member,
        status=status,
    )
    booking.full_clean()
    booking.save()
    if status == Booking.Status.BOOKED:
        _enqueue_class_booking_notification(booking)
    return booking


def _enqueue_class_booking_notification(booking):
    """CLASS_BOOKING is recorded after commit so notify failure cannot undo the booking."""

    def _notify():
        try:
            from notifications.models import NotificationChannel, NotificationEventType
            from notifications.services import enqueue_notification

            enqueue_notification(
                organization=booking.organization,
                member=booking.member,
                event_type=NotificationEventType.CLASS_BOOKING,
                channel=NotificationChannel.IN_APP,
                context={"booking_id": str(booking.uuid)},
            )
        except Exception:
            pass

    transaction.on_commit(_notify)


@transaction.atomic
def cancel_booking(*, booking_id):
    booking = Booking.objects.select_for_update().select_related("occurrence").get(pk=booking_id)
    if booking.status == Booking.Status.CANCELLED:
        raise BookingError("ALREADY_CANCELLED", "This booking is already cancelled.")
    if booking.status not in (Booking.Status.BOOKED, Booking.Status.WAITLISTED):
        raise BookingError("CANNOT_CANCEL", f"Cannot cancel a booking in status {booking.status!r}.")
    booking.status = Booking.Status.CANCELLED
    booking.cancelled_at = timezone.now()
    booking.save(update_fields=["status", "cancelled_at", "updated_at"])
    return booking


@transaction.atomic
def create_occurrence(*, gym_class, start_time, end_time, capacity_override=None):
    """Staff-scheduled session. Trainer conflict is decided here (REQ-041)."""
    if end_time <= start_time:
        raise BookingError("INVALID_WINDOW", "end_time must be after start_time.")
    if gym_class.trainer_id and trainer_has_overlapping_hold(
        trainer_id=gym_class.trainer_id, start_time=start_time, end_time=end_time
    ):
        raise BookingError("TRAINER_CONFLICT", "The trainer has a conflicting session at this time.")
    occurrence = ClassOccurrence(
        organization=gym_class.organization,
        gym_class=gym_class,
        start_time=start_time,
        end_time=end_time,
        capacity_override=capacity_override,
        status=ClassOccurrence.Status.SCHEDULED,
    )
    occurrence.full_clean()
    occurrence.save()
    return occurrence


@transaction.atomic
def cancel_occurrence(*, occurrence_id):
    occurrence = ClassOccurrence.objects.select_for_update().get(pk=occurrence_id)
    if occurrence.status == ClassOccurrence.Status.CANCELLED:
        raise BookingError("ALREADY_CANCELLED", "This class session is already cancelled.")
    if Booking.objects.filter(occurrence=occurrence, status=Booking.Status.BOOKED).exists():
        raise BookingError(
            "HAS_BOOKINGS",
            "Cancel existing bookings before cancelling this class session.",
        )
    occurrence.status = ClassOccurrence.Status.CANCELLED
    occurrence.save(update_fields=["status", "updated_at"])
    return occurrence
