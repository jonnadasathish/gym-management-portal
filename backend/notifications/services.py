"""Enqueue and locally deliver notifications (in-app / console log only)."""

import logging
from datetime import timedelta

from django.utils import timezone

from classes.models import Booking, ClassOccurrence
from members.models import Member
from memberships.models import Membership
from memberships.services import expire_overdue_memberships
from notifications.models import (
    NotificationChannel,
    NotificationEventType,
    NotificationLog,
    NotificationTemplate,
)
from notifications.providers import ConsoleNotificationProvider, NotificationProvider
from pt.models import PTSession

logger = logging.getLogger(__name__)


def get_default_provider() -> NotificationProvider:
    """V1 uses the console/log provider for every channel (OQ-001/002)."""

    return ConsoleNotificationProvider()


def enqueue_notification(
    *,
    organization,
    event_type,
    channel=NotificationChannel.IN_APP,
    member=None,
    user=None,
    context=None,
    provider=None,
):
    """Render a template (or a default event_type string) and deliver locally.

    For IN_APP and the console provider: call `provider.send` and persist a
    `NotificationLog` with status SENT. Never performs external HTTP.
    """

    if member is not None and member.organization_id != organization.id:
        raise ValueError("member.organization must match organization.")
    if user is not None and user.organization_id != organization.id:
        raise ValueError("user.organization must match organization.")

    payload = dict(context or {})
    body = _render_body(organization=organization, event_type=event_type, channel=channel, context=payload)
    recipient_user = user
    if recipient_user is None and member is not None:
        recipient_user = getattr(member, "user", None)

    to = _destination(user=recipient_user, member=member)
    metadata = {
        "event_type": event_type,
        "channel": channel,
        "organization_id": str(organization.uuid),
    }
    active_provider = provider or get_default_provider()

    try:
        message_id = active_provider.send(to=to, body=body, metadata=metadata)
    except Exception as exc:
        return NotificationLog.objects.create(
            organization=organization,
            recipient_member=member,
            recipient_user=recipient_user,
            event_type=event_type,
            channel=channel,
            status=NotificationLog.Status.FAILED,
            error_detail=str(exc),
            payload=payload,
        )

    return NotificationLog.objects.create(
        organization=organization,
        recipient_member=member,
        recipient_user=recipient_user,
        event_type=event_type,
        channel=channel,
        status=NotificationLog.Status.SENT,
        provider_message_id=message_id,
        sent_at=timezone.now(),
        payload=payload,
    )


def emit_membership_expiring_reminders(*, as_of=None, days=7):
    """Enqueue IN_APP MEMBERSHIP_EXPIRING for ACTIVE memberships ending soon.

    Window is inclusive: end_date in [as_of.date(), as_of.date() + days].
    Idempotent on organization + event_type + recipient_member + membership_id.
    """

    as_of = as_of or timezone.now()
    window_start = as_of.date()
    window_end = window_start + timedelta(days=days)
    memberships = Membership.objects.filter(
        status=Membership.Status.ACTIVE,
        end_date__gte=window_start,
        end_date__lte=window_end,
    ).select_related("member", "organization")
    created = []
    for membership in memberships:
        membership_id = str(membership.uuid)
        if _already_enqueued(
            organization=membership.organization,
            event_type=NotificationEventType.MEMBERSHIP_EXPIRING,
            recipient_member=membership.member,
            payload_key="membership_id",
            resource_id=membership_id,
        ):
            continue
        log = _enqueue_reminder(
            organization=membership.organization,
            event_type=NotificationEventType.MEMBERSHIP_EXPIRING,
            member=membership.member,
            context={
                "membership_id": membership_id,
                "end_date": membership.end_date.isoformat(),
            },
        )
        if log is not None:
            created.append(log)
    return created


def emit_class_reminders(*, as_of=None, hours=24):
    """Enqueue IN_APP CLASS_REMINDER for BOOKED sessions starting soon.

    Window is (as_of, as_of + hours]. Waitlisted bookings are excluded.
    Idempotent on organization + event_type + recipient_member + booking_id.
    """

    as_of = as_of or timezone.now()
    window_end = as_of + timedelta(hours=hours)
    bookings = Booking.objects.filter(
        status=Booking.Status.BOOKED,
        occurrence__status=ClassOccurrence.Status.SCHEDULED,
        occurrence__start_time__gt=as_of,
        occurrence__start_time__lte=window_end,
    ).select_related("member", "organization", "occurrence")
    created = []
    for booking in bookings:
        booking_id = str(booking.uuid)
        if _already_enqueued(
            organization=booking.organization,
            event_type=NotificationEventType.CLASS_REMINDER,
            recipient_member=booking.member,
            payload_key="booking_id",
            resource_id=booking_id,
        ):
            continue
        log = _enqueue_reminder(
            organization=booking.organization,
            event_type=NotificationEventType.CLASS_REMINDER,
            member=booking.member,
            context={
                "booking_id": booking_id,
                "occurrence_id": str(booking.occurrence.uuid),
                "start_time": booking.occurrence.start_time.isoformat(),
            },
        )
        if log is not None:
            created.append(log)
    return created


def emit_pt_reminders(*, as_of=None, hours=24):
    """Enqueue IN_APP PT_REMINDER for SCHEDULED PT sessions starting soon.

    Window is (as_of, as_of + hours]. Idempotent on organization + event_type
    + recipient_member + session_id.
    """

    as_of = as_of or timezone.now()
    window_end = as_of + timedelta(hours=hours)
    sessions = PTSession.objects.filter(
        status=PTSession.Status.SCHEDULED,
        scheduled_at__gt=as_of,
        scheduled_at__lte=window_end,
    ).select_related("member", "organization")
    created = []
    for session in sessions:
        session_id = str(session.uuid)
        if _already_enqueued(
            organization=session.organization,
            event_type=NotificationEventType.PT_REMINDER,
            recipient_member=session.member,
            payload_key="session_id",
            resource_id=session_id,
        ):
            continue
        log = _enqueue_reminder(
            organization=session.organization,
            event_type=NotificationEventType.PT_REMINDER,
            member=session.member,
            context={
                "session_id": session_id,
                "scheduled_at": session.scheduled_at.isoformat(),
            },
        )
        if log is not None:
            created.append(log)
    return created


def emit_membership_expired_reminders(*, as_of=None):
    """Expire overdue ACTIVE memberships, then enqueue IN_APP MEMBERSHIP_EXPIRED.

    Idempotent on organization + event_type + recipient_member + membership_id.
    FROZEN and CANCELLED memberships are not expired or notified here.
    """

    as_of = as_of or timezone.now()
    expire_overdue_memberships(as_of=as_of)
    memberships = Membership.objects.filter(
        status=Membership.Status.EXPIRED,
        end_date__lt=as_of.date(),
    ).select_related("member", "organization")
    created = []
    for membership in memberships:
        membership_id = str(membership.uuid)
        if _already_enqueued(
            organization=membership.organization,
            event_type=NotificationEventType.MEMBERSHIP_EXPIRED,
            recipient_member=membership.member,
            payload_key="membership_id",
            resource_id=membership_id,
        ):
            continue
        log = _enqueue_reminder(
            organization=membership.organization,
            event_type=NotificationEventType.MEMBERSHIP_EXPIRED,
            member=membership.member,
            context={
                "membership_id": membership_id,
                "end_date": membership.end_date.isoformat(),
            },
        )
        if log is not None:
            created.append(log)
    return created


def emit_birthday_reminders(*, as_of=None):
    """Enqueue IN_APP BIRTHDAY for members whose dob month/day matches as_of.

    Year is ignored. Only an exact month/day match notifies (no Feb 29 fallback).
    Members without dob are skipped. Idempotent per member per calendar day via
    payload birthday_on.
    """

    as_of = as_of or timezone.now()
    today = as_of.date()
    birthday_on = today.isoformat()
    members = Member.objects.filter(
        dob__isnull=False,
        dob__month=today.month,
        dob__day=today.day,
    ).select_related("organization")
    created = []
    for member in members:
        if _already_enqueued(
            organization=member.organization,
            event_type=NotificationEventType.BIRTHDAY,
            recipient_member=member,
            payload_key="birthday_on",
            resource_id=birthday_on,
        ):
            continue
        log = _enqueue_reminder(
            organization=member.organization,
            event_type=NotificationEventType.BIRTHDAY,
            member=member,
            context={"birthday_on": birthday_on},
        )
        if log is not None:
            created.append(log)
    return created


def _already_enqueued(*, organization, event_type, recipient_member, payload_key, resource_id):
    logs = NotificationLog.objects.filter(
        organization=organization,
        event_type=event_type,
        recipient_member=recipient_member,
    )
    return any(
        str((payload or {}).get(payload_key, "")) == str(resource_id)
        for payload in logs.values_list("payload", flat=True)
    )


def _enqueue_reminder(*, organization, event_type, member, context):
    try:
        return enqueue_notification(
            organization=organization,
            event_type=event_type,
            channel=NotificationChannel.IN_APP,
            member=member,
            context=context,
        )
    except Exception:
        logger.exception(
            "reminder enqueue failed event_type=%s member_id=%s",
            event_type,
            getattr(member, "pk", None),
        )
        return None


def _render_body(*, organization, event_type, channel, context):
    template = (
        NotificationTemplate.objects.for_organization(organization)
        .filter(event_type=event_type, channel=channel, is_active=True)
        .first()
    )
    if template is None:
        return str(event_type)
    return _format_template(template.body, context)


def _format_template(body, context):
    try:
        return body.format(**context)
    except (KeyError, IndexError, ValueError):
        return body


def _destination(*, user, member):
    if user is not None:
        return user.email or user.phone or str(user.uuid)
    if member is not None:
        return member.phone or member.email or str(member.uuid)
    return ""
