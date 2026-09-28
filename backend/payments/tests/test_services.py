import hashlib
import hmac
from decimal import Decimal

import pytest

from accounts.tests.factories import UserFactory
from billing.models import Invoice
from billing.tests.factories import InvoiceFactory
from payments.models import Payment, PaymentEvent, Refund
from payments.providers import FakePaymentProvider, RazorpayProvider
from payments.services import (
    DuplicateWebhookEvent,
    PaymentStateError,
    handle_webhook_event,
    initiate_gateway_payment,
    process_refund,
    record_cash_payment,
)

pytestmark = pytest.mark.django_db


def _signed(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def test_record_cash_payment_marks_invoice_paid():
    invoice = InvoiceFactory(total=Decimal("2000.00"), status=Invoice.Status.ISSUED)
    staff = UserFactory(organization=invoice.organization)

    payment = record_cash_payment(
        invoice_id=invoice.id,
        amount=Decimal("2000.00"),
        method=Payment.Method.CASH,
        recorded_by=staff,
    )

    invoice.refresh_from_db()
    assert payment.status == Payment.Status.SUCCESSFUL
    assert payment.amount == Decimal("2000.00")
    assert invoice.status == Invoice.Status.PAID


def test_record_cash_payment_partial_marks_invoice_partially_paid():
    invoice = InvoiceFactory(total=Decimal("2000.00"), status=Invoice.Status.ISSUED)
    record_cash_payment(
        invoice_id=invoice.id,
        amount=Decimal("800.00"),
        method=Payment.Method.UPI,
        recorded_by=None,
    )
    invoice.refresh_from_db()
    assert invoice.status == Invoice.Status.PARTIALLY_PAID


def test_record_cash_payment_idempotency_key_returns_same_row():
    invoice = InvoiceFactory(total=Decimal("2000.00"))
    first = record_cash_payment(
        invoice_id=invoice.id,
        amount=Decimal("2000.00"),
        method=Payment.Method.CASH,
        recorded_by=None,
        idempotency_key="cash-abc-1",
    )
    second = record_cash_payment(
        invoice_id=invoice.id,
        amount=Decimal("2000.00"),
        method=Payment.Method.CASH,
        recorded_by=None,
        idempotency_key="cash-abc-1",
    )
    assert first.id == second.id
    assert Payment.objects.filter(invoice=invoice).count() == 1


def test_initiate_gateway_payment_creates_initiated_row_via_provider():
    invoice = InvoiceFactory(total=Decimal("2000.00"))
    provider = FakePaymentProvider()

    payment = initiate_gateway_payment(invoice_id=invoice.id, amount=Decimal("2000.00"), provider=provider)

    assert payment.status == Payment.Status.INITIATED
    assert payment.method == Payment.Method.GATEWAY
    assert payment.gateway == "RAZORPAY"
    assert payment.gateway_order_id == "order_fake_1"
    assert len(provider.created_orders) == 1


def test_webhook_success_updates_payment_and_invoice():
    invoice = InvoiceFactory(total=Decimal("2000.00"), status=Invoice.Status.ISSUED)
    provider = FakePaymentProvider()
    payment = initiate_gateway_payment(invoice_id=invoice.id, amount=Decimal("2000.00"), provider=provider)
    body = b'{"event":"payment.captured"}'
    secret = "whsec"

    updated = handle_webhook_event(
        provider=provider,
        payload_body=body,
        signature=_signed(body, secret),
        webhook_secret=secret,
        gateway_event_id="evt_1",
        event_type="payment.captured",
        gateway_order_id=payment.gateway_order_id,
        new_status=Payment.Status.SUCCESSFUL,
        raw_payload={"event": "payment.captured"},
    )

    invoice.refresh_from_db()
    assert updated.status == Payment.Status.SUCCESSFUL
    assert updated.paid_at is not None
    assert invoice.status == Invoice.Status.PAID
    assert PaymentEvent.objects.filter(gateway_event_id="evt_1").count() == 1


def test_duplicate_webhook_does_not_create_second_event_or_side_effect():
    invoice = InvoiceFactory(total=Decimal("2000.00"), status=Invoice.Status.ISSUED)
    provider = FakePaymentProvider()
    payment = initiate_gateway_payment(invoice_id=invoice.id, amount=Decimal("2000.00"), provider=provider)
    body = b'{"event":"payment.captured"}'
    secret = "whsec"
    kwargs = dict(
        provider=provider,
        payload_body=body,
        signature=_signed(body, secret),
        webhook_secret=secret,
        gateway_event_id="evt_dup",
        event_type="payment.captured",
        gateway_order_id=payment.gateway_order_id,
        new_status=Payment.Status.SUCCESSFUL,
    )

    handle_webhook_event(**kwargs)
    with pytest.raises(DuplicateWebhookEvent):
        handle_webhook_event(**kwargs)

    assert PaymentEvent.objects.filter(gateway_event_id="evt_dup").count() == 1
    payment.refresh_from_db()
    assert payment.status == Payment.Status.SUCCESSFUL


def test_invalid_webhook_signature_is_rejected():
    invoice = InvoiceFactory()
    provider = FakePaymentProvider()
    payment = initiate_gateway_payment(invoice_id=invoice.id, amount=Decimal("2000.00"), provider=provider)

    with pytest.raises(PaymentStateError):
        handle_webhook_event(
            provider=provider,
            payload_body=b"{}",
            signature="not-a-valid-hmac",
            webhook_secret="whsec",
            gateway_event_id="evt_bad",
            event_type="payment.captured",
            gateway_order_id=payment.gateway_order_id,
            new_status=Payment.Status.SUCCESSFUL,
        )

    payment.refresh_from_db()
    assert payment.status == Payment.Status.INITIATED
    assert PaymentEvent.objects.filter(gateway_event_id="evt_bad").count() == 0


def test_razorpay_hmac_verification_accepts_valid_and_rejects_tampered():
    provider = RazorpayProvider(key_id="rzp_test", key_secret="unused")
    body = b'{"id":"evt_x"}'
    secret = "hook-secret"
    good = _signed(body, secret)
    assert provider.verify_webhook_signature(payload_body=body, signature=good, secret=secret) is True
    assert provider.verify_webhook_signature(payload_body=body, signature="deadbeef", secret=secret) is False


def test_full_refund_marks_payment_refunded_without_mutating_amount():
    invoice = InvoiceFactory(total=Decimal("2000.00"))
    payment = record_cash_payment(
        invoice_id=invoice.id, amount=Decimal("2000.00"), method=Payment.Method.CASH, recorded_by=None
    )
    provider = FakePaymentProvider()

    refund = process_refund(
        payment_id=payment.id,
        amount=Decimal("2000.00"),
        reason="Member cancelled",
        initiated_by=None,
        provider=provider,
    )

    payment.refresh_from_db()
    assert refund.status == Refund.Status.PROCESSED
    assert payment.amount == Decimal("2000.00")
    assert payment.status == Payment.Status.REFUNDED


def test_partial_refund_marks_partially_refunded():
    invoice = InvoiceFactory(total=Decimal("2000.00"))
    payment = record_cash_payment(
        invoice_id=invoice.id, amount=Decimal("2000.00"), method=Payment.Method.CASH, recorded_by=None
    )
    process_refund(
        payment_id=payment.id,
        amount=Decimal("500.00"),
        reason="Partial correction",
        initiated_by=None,
        provider=FakePaymentProvider(),
    )
    payment.refresh_from_db()
    invoice.refresh_from_db()
    assert payment.status == Payment.Status.PARTIALLY_REFUNDED
    assert payment.amount == Decimal("2000.00")
    assert invoice.status == Invoice.Status.PARTIALLY_PAID


def test_full_refund_returns_invoice_to_issued():
    invoice = InvoiceFactory(total=Decimal("2000.00"))
    payment = record_cash_payment(
        invoice_id=invoice.id, amount=Decimal("2000.00"), method=Payment.Method.CASH, recorded_by=None
    )
    process_refund(
        payment_id=payment.id,
        amount=Decimal("2000.00"),
        reason="Member cancelled",
        initiated_by=None,
        provider=FakePaymentProvider(),
    )
    invoice.refresh_from_db()
    assert invoice.status == Invoice.Status.ISSUED


def test_refund_cannot_exceed_original_amount():
    invoice = InvoiceFactory(total=Decimal("1000.00"))
    payment = record_cash_payment(
        invoice_id=invoice.id, amount=Decimal("1000.00"), method=Payment.Method.CASH, recorded_by=None
    )
    with pytest.raises(PaymentStateError):
        process_refund(
            payment_id=payment.id,
            amount=Decimal("1000.01"),
            reason="too much",
            initiated_by=None,
            provider=FakePaymentProvider(),
        )


def test_cannot_refund_non_successful_payment():
    invoice = InvoiceFactory()
    provider = FakePaymentProvider()
    payment = initiate_gateway_payment(invoice_id=invoice.id, amount=Decimal("100.00"), provider=provider)
    with pytest.raises(PaymentStateError):
        process_refund(
            payment_id=payment.id,
            amount=Decimal("100.00"),
            reason="n/a",
            initiated_by=None,
            provider=provider,
        )
