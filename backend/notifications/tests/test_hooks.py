"""Domain-service notification hooks (PRD transactional events, in-app only)."""

import datetime
import hashlib
import hmac
from decimal import Decimal

import pytest
from django.utils import timezone

from billing.tests.factories import InvoiceFactory
from classes.models import Booking
from classes.services import book_occurrence
from classes.tests.factories import ClassOccurrenceFactory, GymClassFactory
from members.tests.factories import MemberFactory
from memberships.models import Membership
from memberships.services import apply_freeze, renew_membership
from memberships.tests.factories import MembershipFactory, MembershipPlanFactory
from notifications.models import NotificationChannel, NotificationEventType, NotificationLog
from organizations.tests.factories import OrganizationFactory
from payments.models import Payment
from payments.providers import FakePaymentProvider
from payments.services import (
    DuplicateWebhookEvent,
    handle_webhook_event,
    initiate_gateway_payment,
    record_cash_payment,
)
from pt.services import schedule_session
from pt.tests.factories import PTPackageFactory

pytestmark = pytest.mark.django_db


def _signed(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def test_book_occurrence_creates_class_booking_log(django_capture_on_commit_callbacks):
    occurrence = ClassOccurrenceFactory()
    member = MemberFactory(organization=occurrence.organization, home_branch=occurrence.gym_class.branch)

    with django_capture_on_commit_callbacks(execute=True):
        booking = book_occurrence(occurrence_id=occurrence.id, member=member)

    log = NotificationLog.objects.get(event_type=NotificationEventType.CLASS_BOOKING)
    assert log.organization_id == occurrence.organization_id
    assert log.recipient_member_id == member.id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["booking_id"] == str(booking.uuid)


def test_waitlisted_booking_does_not_create_class_booking_log(django_capture_on_commit_callbacks):
    gym_class = GymClassFactory(capacity=1)
    occurrence = ClassOccurrenceFactory(gym_class=gym_class, organization=gym_class.organization)
    m1 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)
    m2 = MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch)

    with django_capture_on_commit_callbacks(execute=True):
        book_occurrence(occurrence_id=occurrence.id, member=m1)
        waitlisted = book_occurrence(occurrence_id=occurrence.id, member=m2, waitlist_if_full=True)

    assert waitlisted.status == Booking.Status.WAITLISTED
    assert NotificationLog.objects.filter(event_type=NotificationEventType.CLASS_BOOKING).count() == 1
    assert not NotificationLog.objects.filter(recipient_member=m2).exists()


def test_apply_freeze_creates_freeze_approved_log(django_capture_on_commit_callbacks):
    membership = MembershipFactory(
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
    )

    with django_capture_on_commit_callbacks(execute=True):
        apply_freeze(
            membership_id=membership.id,
            start_date=datetime.date(2026, 1, 10),
            end_date=datetime.date(2026, 1, 15),
            reason="Travel",
            requested_by=None,
        )

    log = NotificationLog.objects.get(event_type=NotificationEventType.FREEZE_APPROVED)
    assert log.organization_id == membership.organization_id
    assert log.recipient_member_id == membership.member_id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["membership_id"] == str(membership.uuid)


def test_record_cash_payment_creates_payment_successful_log(django_capture_on_commit_callbacks):
    invoice = InvoiceFactory(total=Decimal("2000.00"))

    with django_capture_on_commit_callbacks(execute=True):
        payment = record_cash_payment(
            invoice_id=invoice.id,
            amount=Decimal("2000.00"),
            method=Payment.Method.CASH,
            recorded_by=None,
        )

    log = NotificationLog.objects.get(event_type=NotificationEventType.PAYMENT_SUCCESSFUL)
    assert log.organization_id == invoice.organization_id
    assert log.recipient_member_id == invoice.member_id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["invoice_id"] == str(invoice.uuid)
    assert log.payload["payment_id"] == str(payment.uuid)


def test_schedule_session_creates_pt_booking_log(django_capture_on_commit_callbacks):
    package = PTPackageFactory()

    with django_capture_on_commit_callbacks(execute=True):
        session = schedule_session(
            package_id=package.id,
            scheduled_at=timezone.now() + datetime.timedelta(days=2),
        )

    log = NotificationLog.objects.get(event_type=NotificationEventType.PT_BOOKING)
    assert log.organization_id == package.organization_id
    assert log.recipient_member_id == package.member_id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["session_id"] == str(session.uuid)


def test_renew_membership_creates_membership_created_log(django_capture_on_commit_callbacks):
    old_membership = MembershipFactory(status=Membership.Status.ACTIVE)
    new_plan = MembershipPlanFactory(organization=old_membership.organization)

    with django_capture_on_commit_callbacks(execute=True):
        new_membership = renew_membership(
            membership_id=old_membership.id,
            new_plan=new_plan,
            new_start_date=old_membership.end_date + datetime.timedelta(days=1),
            new_end_date=old_membership.end_date + datetime.timedelta(days=31),
            price=Decimal("2200.00"),
            discount=Decimal("0.00"),
            created_by=None,
        )

    log = NotificationLog.objects.get(event_type=NotificationEventType.MEMBERSHIP_CREATED)
    assert log.recipient_member_id == new_membership.member_id
    assert log.payload["membership_id"] == str(new_membership.uuid)


def test_membership_serializer_create_enqueues_membership_created(django_capture_on_commit_callbacks):
    from types import SimpleNamespace

    from accounts.tests.factories import OwnerFactory
    from branches.tests.factories import BranchFactory
    from memberships.serializers import MembershipSerializer

    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member = MemberFactory(organization=owner.organization, home_branch=branch)
    plan = MembershipPlanFactory(organization=owner.organization)
    serializer = MembershipSerializer(
        data={
            "member_id": str(member.uuid),
            "plan_id": str(plan.uuid),
            "start_date": "2026-09-01",
        },
        context={"request": SimpleNamespace(user=owner)},
    )
    assert serializer.is_valid(), serializer.errors

    with django_capture_on_commit_callbacks(execute=True):
        membership = serializer.save()

    log = NotificationLog.objects.get(event_type=NotificationEventType.MEMBERSHIP_CREATED)
    assert log.recipient_member_id == member.id
    assert log.payload["membership_id"] == str(membership.uuid)


def test_webhook_first_success_creates_payment_successful_log(django_capture_on_commit_callbacks):
    invoice = InvoiceFactory(total=Decimal("2000.00"))
    provider = FakePaymentProvider()
    payment = initiate_gateway_payment(invoice_id=invoice.id, amount=Decimal("2000.00"), provider=provider)
    body = b'{"event":"payment.captured"}'

    with django_capture_on_commit_callbacks(execute=True):
        handle_webhook_event(
            provider=provider,
            payload_body=body,
            signature=_signed(body, "whsec"),
            webhook_secret="whsec",
            gateway_event_id="evt_notify_1",
            event_type="payment.captured",
            gateway_order_id=payment.gateway_order_id,
            new_status=Payment.Status.SUCCESSFUL,
        )

    assert NotificationLog.objects.filter(event_type=NotificationEventType.PAYMENT_SUCCESSFUL).count() == 1


def test_duplicate_webhook_does_not_create_second_payment_log(django_capture_on_commit_callbacks):
    invoice = InvoiceFactory(total=Decimal("2000.00"))
    provider = FakePaymentProvider()
    payment = initiate_gateway_payment(invoice_id=invoice.id, amount=Decimal("2000.00"), provider=provider)
    body = b'{"event":"payment.captured"}'
    kwargs = dict(
        provider=provider,
        payload_body=body,
        signature=_signed(body, "whsec"),
        webhook_secret="whsec",
        gateway_event_id="evt_notify_dup",
        event_type="payment.captured",
        gateway_order_id=payment.gateway_order_id,
        new_status=Payment.Status.SUCCESSFUL,
    )

    with django_capture_on_commit_callbacks(execute=True):
        handle_webhook_event(**kwargs)
    with pytest.raises(DuplicateWebhookEvent):
        with django_capture_on_commit_callbacks(execute=True):
            handle_webhook_event(**kwargs)

    assert NotificationLog.objects.filter(event_type=NotificationEventType.PAYMENT_SUCCESSFUL).count() == 1


def test_webhook_first_failed_creates_payment_failed_log_duplicate_does_not(django_capture_on_commit_callbacks):
    invoice = InvoiceFactory(total=Decimal("2000.00"))
    provider = FakePaymentProvider()
    payment = initiate_gateway_payment(invoice_id=invoice.id, amount=Decimal("2000.00"), provider=provider)
    body = b'{"event":"payment.failed"}'
    kwargs = dict(
        provider=provider,
        payload_body=body,
        signature=_signed(body, "whsec"),
        webhook_secret="whsec",
        gateway_event_id="evt_notify_fail_dup",
        event_type="payment.failed",
        gateway_order_id=payment.gateway_order_id,
        new_status=Payment.Status.FAILED,
    )

    with django_capture_on_commit_callbacks(execute=True):
        handle_webhook_event(**kwargs)

    log = NotificationLog.objects.get(event_type=NotificationEventType.PAYMENT_FAILED)
    assert log.organization_id == invoice.organization_id
    assert log.recipient_member_id == invoice.member_id
    assert log.channel == NotificationChannel.IN_APP
    assert log.payload["invoice_id"] == str(invoice.uuid)
    assert log.payload["payment_id"] == str(payment.uuid)

    with pytest.raises(DuplicateWebhookEvent):
        with django_capture_on_commit_callbacks(execute=True):
            handle_webhook_event(**kwargs)

    assert NotificationLog.objects.filter(event_type=NotificationEventType.PAYMENT_FAILED).count() == 1
    payment.refresh_from_db()
    assert payment.status == Payment.Status.FAILED


def test_org_b_does_not_receive_org_a_class_booking_notification(django_capture_on_commit_callbacks):
    occurrence = ClassOccurrenceFactory()
    member_a = MemberFactory(organization=occurrence.organization, home_branch=occurrence.gym_class.branch)
    org_b = OrganizationFactory()

    with django_capture_on_commit_callbacks(execute=True):
        book_occurrence(occurrence_id=occurrence.id, member=member_a)

    assert NotificationLog.objects.for_organization(occurrence.organization).filter(
        event_type=NotificationEventType.CLASS_BOOKING
    ).exists()
    assert not NotificationLog.objects.for_organization(org_b).exists()
