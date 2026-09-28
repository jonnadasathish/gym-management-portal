"""Payment business logic (AGENTS.md §21, DEC-018, DEC-020).

Every status transition on `Payment` MUST go through this module — views/
serializers must never set `.status` directly (AGENTS.md §15.1 layering).
"""

from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone

from billing.models import Invoice
from payments.models import Payment, PaymentEvent, Refund


class PaymentStateError(Exception):
    pass


class DuplicateWebhookEvent(Exception):
    """Raised (and safely swallowed by the caller) when a webhook with an
    already-seen `gateway_event_id` is received — REQ-035/§59.5: a
    duplicate webhook must not produce duplicate financial side effects."""


def _recompute_invoice_status(invoice: Invoice):
    """Net collected = credited payment amounts minus processed refunds.

    Payments that have been fully or partially refunded still keep their
    original amount (financial-history immutability, AGENTS.md §21.6), so
    invoice status must be derived from net collected, not from
    SUCCESSFUL rows alone.
    """

    if invoice.status == Invoice.Status.VOID:
        return

    credited = invoice.payments.filter(
        status__in=(
            Payment.Status.SUCCESSFUL,
            Payment.Status.PARTIALLY_REFUNDED,
            Payment.Status.REFUNDED,
        )
    ).aggregate(total=models_sum("amount"))["total"] or Decimal("0.00")
    refunded = Refund.objects.filter(
        payment__invoice=invoice, status=Refund.Status.PROCESSED
    ).aggregate(total=models_sum("amount"))["total"] or Decimal("0.00")
    total_paid = credited - refunded

    if total_paid <= 0:
        invoice.status = Invoice.Status.ISSUED
    elif total_paid >= invoice.total:
        invoice.status = Invoice.Status.PAID
    else:
        invoice.status = Invoice.Status.PARTIALLY_PAID
    invoice.save(update_fields=["status", "updated_at"])


def models_sum(field):
    from django.db.models import Sum

    return Sum(field)


@transaction.atomic
def record_cash_payment(*, invoice_id, amount, method, recorded_by, idempotency_key=None):
    """Cash/UPI/card payments collected in person — settle immediately
    (AGENTS.md §21.1 "cash" is a first-class supported method)."""

    if idempotency_key:
        existing = Payment.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

    invoice = Invoice.objects.select_for_update().select_related("organization", "member").get(pk=invoice_id)

    payment = Payment.objects.create(
        organization=invoice.organization,
        invoice=invoice,
        amount=amount,
        method=method,
        status=Payment.Status.SUCCESSFUL,
        paid_at=timezone.now(),
        recorded_by=recorded_by,
        idempotency_key=idempotency_key,
    )
    _recompute_invoice_status(invoice)
    _enqueue_payment_successful_notification(payment=payment, invoice=invoice)
    return payment


@transaction.atomic
def initiate_gateway_payment(*, invoice_id, amount, provider, gateway_name="RAZORPAY"):
    """Create a gateway order and a PENDING Payment row awaiting webhook
    confirmation. See payments.providers module docstring for the
    real-network test-coverage caveat on `provider.create_order`."""

    invoice = Invoice.objects.select_related("organization").get(pk=invoice_id)
    order = provider.create_order(amount=amount, currency=invoice.organization.default_currency, receipt=invoice.invoice_number)

    payment = Payment.objects.create(
        organization=invoice.organization,
        invoice=invoice,
        amount=amount,
        method=Payment.Method.GATEWAY,
        gateway=gateway_name,
        gateway_order_id=order["gateway_order_id"],
        status=Payment.Status.INITIATED,
    )
    return payment


@transaction.atomic
def handle_webhook_event(*, provider, payload_body: bytes, signature: str, webhook_secret: str, gateway_event_id, event_type, gateway_order_id, new_status, raw_payload=None):
    """Idempotent webhook handler (REQ-035, DEC-018, §59.5). The
    idempotency guard is the DB-level unique constraint on
    `PaymentEvent.gateway_event_id`, not merely an application-level
    check-then-insert — a duplicate webhook racing in concurrently still
    cannot create two events for the same gateway_event_id.
    """

    if not provider.verify_webhook_signature(payload_body=payload_body, signature=signature, secret=webhook_secret):
        raise PaymentStateError("Invalid webhook signature.")

    payment = Payment.objects.select_for_update().select_related("invoice", "invoice__member").get(
        gateway_order_id=gateway_order_id
    )
    previous_status = payment.status

    try:
        with transaction.atomic():
            event = PaymentEvent.objects.create(
                payment=payment,
                event_type=event_type,
                gateway_event_id=gateway_event_id,
                raw_payload=raw_payload or {},
            )
    except IntegrityError:
        # gateway_event_id already processed — duplicate webhook delivery.
        # No financial side effect is (re)applied. This is expected
        # gateway retry behavior, not an error condition to surface loudly.
        raise DuplicateWebhookEvent(gateway_event_id)

    payment.status = new_status
    if new_status == Payment.Status.SUCCESSFUL:
        payment.paid_at = timezone.now()
    payment.save(update_fields=["status", "paid_at", "updated_at"])

    event.processed_at = timezone.now()
    event.save(update_fields=["processed_at"])

    if new_status == Payment.Status.SUCCESSFUL:
        _recompute_invoice_status(payment.invoice)
        if previous_status != Payment.Status.SUCCESSFUL:
            _enqueue_payment_successful_notification(payment=payment, invoice=payment.invoice)
    elif new_status == Payment.Status.FAILED and previous_status != Payment.Status.FAILED:
        _enqueue_payment_failed_notification(payment=payment, invoice=payment.invoice)

    return payment


def _enqueue_payment_successful_notification(*, payment, invoice):
    """PAYMENT_SUCCESSFUL is recorded after commit so notify failure cannot undo settlement."""

    def _notify():
        try:
            from notifications.models import NotificationChannel, NotificationEventType
            from notifications.services import enqueue_notification

            enqueue_notification(
                organization=invoice.organization,
                member=invoice.member,
                event_type=NotificationEventType.PAYMENT_SUCCESSFUL,
                channel=NotificationChannel.IN_APP,
                context={
                    "invoice_id": str(invoice.uuid),
                    "payment_id": str(payment.uuid),
                },
            )
        except Exception:
            pass

    transaction.on_commit(_notify)


def _enqueue_payment_failed_notification(*, payment, invoice):
    """PAYMENT_FAILED is recorded after commit so notify failure cannot undo the FAILED status."""

    def _notify():
        try:
            from notifications.models import NotificationChannel, NotificationEventType
            from notifications.services import enqueue_notification

            enqueue_notification(
                organization=invoice.organization,
                member=invoice.member,
                event_type=NotificationEventType.PAYMENT_FAILED,
                channel=NotificationChannel.IN_APP,
                context={
                    "invoice_id": str(invoice.uuid),
                    "payment_id": str(payment.uuid),
                },
            )
        except Exception:
            pass

    transaction.on_commit(_notify)


@transaction.atomic
def process_refund(*, payment_id, amount, reason, initiated_by, provider):
    """Full or partial refund. Never mutates the original Payment amount
    — creates a Refund row and moves Payment to REFUNDED/PARTIALLY_REFUNDED
    (AGENTS.md §21.6, financial-history immutability)."""

    payment = Payment.objects.select_for_update().select_related("invoice").get(pk=payment_id)

    if payment.status not in (Payment.Status.SUCCESSFUL, Payment.Status.PARTIALLY_REFUNDED):
        raise PaymentStateError(f"Cannot refund a payment in status {payment.status!r}.")

    already_refunded = payment.refunds.filter(status=Refund.Status.PROCESSED).aggregate(
        total=models_sum("amount")
    )["total"] or Decimal("0.00")

    if already_refunded + amount > payment.amount:
        raise PaymentStateError("Refund amount would exceed the original payment amount.")

    gateway_result = {}
    if payment.gateway_payment_id:
        gateway_result = provider.process_refund(gateway_payment_id=payment.gateway_payment_id, amount=amount)

    refund = Refund.objects.create(
        payment=payment,
        amount=amount,
        reason=reason,
        status=Refund.Status.PROCESSED,
        gateway_refund_id=gateway_result.get("gateway_refund_id", ""),
        initiated_by=initiated_by,
        processed_at=timezone.now(),
    )

    total_refunded = already_refunded + amount
    payment.status = Payment.Status.REFUNDED if total_refunded >= payment.amount else Payment.Status.PARTIALLY_REFUNDED
    payment.save(update_fields=["status", "updated_at"])

    _recompute_invoice_status(payment.invoice)
    from audit.services import audit_log

    audit_log(
        organization=payment.organization,
        actor=initiated_by,
        action="PAYMENT_REFUND",
        resource_type="payments.Payment",
        resource_uuid=payment.uuid,
        after={"refund_amount": str(amount), "reason": reason},
    )
    return refund
