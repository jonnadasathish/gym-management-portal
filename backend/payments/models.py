"""Payment models. See PROJECT_CONTEXT.md §27.A, §21, DEC-018, REQ-031..037.

Financial-integrity rule enforced throughout this module (AGENTS.md
§15.4/§21.7/§34.4, non-negotiable): every money field is `DecimalField`;
`Payment` rows are never hard-deleted, and once `SUCCESSFUL` are never
directly mutated to a different amount — corrections happen via `Refund`
and `PaymentEvent` rows only. `payments/services.py` is the only code path
permitted to transition a Payment's status.
"""

from decimal import Decimal

from django.db import models

from core.models import TenantScopedModel


class Payment(TenantScopedModel):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"
        GATEWAY = "GATEWAY", "Online gateway"

    class Status(models.TextChoices):
        """Full PRD state set (§21.2/§59.5-6) — never collapsed."""

        PENDING = "PENDING", "Pending"
        INITIATED = "INITIATED", "Initiated"
        SUCCESSFUL = "SUCCESSFUL", "Successful"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"
        PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED", "Partially refunded"
        CANCELLED = "CANCELLED", "Cancelled"

    invoice = models.ForeignKey("billing.Invoice", on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices)
    gateway = models.CharField(max_length=20, blank=True, help_text="e.g. RAZORPAY. Blank for CASH/offline UPI.")
    gateway_payment_id = models.CharField(max_length=100, blank=True, db_index=True)
    gateway_order_id = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments_recorded"
    )
    idempotency_key = models.CharField(max_length=100, blank=True, null=True, unique=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "status"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment({self.id}, {self.amount}, {self.status})"


class PaymentEvent(models.Model):
    """Append-only ledger of state transitions, especially webhook
    deliveries. `gateway_event_id` unique index is the PRIMARY idempotency
    guard against duplicate webhooks (REQ-035/§59.5)."""

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=50)
    gateway_event_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-received_at"]

    def __str__(self):
        return f"PaymentEvent({self.payment_id}, {self.event_type})"


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSED = "PROCESSED", "Processed"
        FAILED = "FAILED", "Failed"

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="refunds")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    gateway_refund_id = models.CharField(max_length=100, blank=True)
    initiated_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="refunds_initiated"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund({self.payment_id}, {self.amount}, {self.status})"


class Subscription(TenantScopedModel):
    """Recurring billing / mandate tracking (REQ-034)."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        PAUSED = "PAUSED", "Paused"
        CANCELLED = "CANCELLED", "Cancelled"

    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="subscriptions")
    membership_plan = models.ForeignKey("memberships.MembershipPlan", on_delete=models.PROTECT, related_name="subscriptions")
    gateway = models.CharField(max_length=20, default="RAZORPAY")
    gateway_subscription_id = models.CharField(max_length=100, db_index=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    next_billing_date = models.DateField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Subscription({self.member_id}, {self.status})"
