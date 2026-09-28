from rest_framework import serializers

from billing.models import Invoice
from payments.models import Payment, Subscription


class PaymentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    invoice = serializers.UUIDField(source="invoice.uuid", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "amount",
            "method",
            "gateway",
            "gateway_order_id",
            "status",
            "paid_at",
        ]
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    """Read-only recurring-billing visibility (REQ-034). No charge/retry."""

    id = serializers.UUIDField(source="uuid", read_only=True)
    member_id = serializers.UUIDField(source="member.uuid", read_only=True)
    plan_name = serializers.CharField(source="membership_plan.name", read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "member_id",
            "plan_name",
            "status",
            "next_billing_date",
            "retry_count",
            "gateway",
        ]
        read_only_fields = fields


class CashPaymentSerializer(serializers.Serializer):
    invoice_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    method = serializers.ChoiceField(choices=[Payment.Method.CASH, Payment.Method.UPI, Payment.Method.CARD])
    idempotency_key = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_invoice_id(self, value):
        org = self.context["request"].user.organization
        try:
            return Invoice.objects.for_organization(org).get(uuid=value)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice not found in your organization.")


class InitiatePaymentSerializer(serializers.Serializer):
    invoice_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)

    def validate_invoice_id(self, value):
        request = self.context["request"]
        org = request.user.organization
        try:
            invoice = Invoice.objects.for_organization(org).select_related("member").get(uuid=value)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice not found in your organization.")
        if request.user.role == "MEMBER" and invoice.member.user_id != request.user.id:
            raise serializers.ValidationError("Invoice not found in your organization.")
        if invoice.status not in (Invoice.Status.ISSUED, Invoice.Status.PARTIALLY_PAID, Invoice.Status.DRAFT):
            raise serializers.ValidationError("Invoice is not payable.")
        return invoice
