from decimal import Decimal

from rest_framework import serializers

from billing.models import Invoice, InvoiceLineItem
from members.models import Member
from memberships.models import Membership


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    related_membership_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = InvoiceLineItem
        fields = [
            "id",
            "description",
            "quantity",
            "unit_price",
            "tax_rate",
            "line_total",
            "related_membership_id",
        ]
        read_only_fields = ["id", "line_total"]


class InvoiceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    member_id = serializers.UUIDField(write_only=True)
    member = serializers.UUIDField(source="member.uuid", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    line_items = InvoiceLineItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "member_id",
            "member",
            "member_name",
            "issue_date",
            "subtotal",
            "discount",
            "tax",
            "total",
            "status",
            "line_items",
        ]
        read_only_fields = ["id", "member", "member_name", "subtotal", "tax", "total", "status", "invoice_number"]

    def validate_member_id(self, value):
        org = self.context["request"].user.organization
        try:
            return Member.objects.for_organization(org).alive().get(uuid=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member not found in your organization.")

    def create(self, validated_data):
        request = self.context["request"]
        member = validated_data.pop("member_id")
        items = validated_data.pop("line_items")
        invoice_number = _next_invoice_number(request.user.organization)
        invoice = Invoice.objects.create(
            organization=request.user.organization,
            member=member,
            invoice_number=invoice_number,
            issue_date=validated_data["issue_date"],
            discount=validated_data.get("discount", 0),
            created_by=request.user,
            status=Invoice.Status.ISSUED,
        )
        for item in items:
            membership = None
            related_id = item.pop("related_membership_id", None)
            if related_id:
                try:
                    membership = Membership.objects.for_organization(request.user.organization).get(uuid=related_id)
                except Membership.DoesNotExist:
                    raise serializers.ValidationError(
                        {"line_items": "related_membership_id not found in your organization."}
                    )
            base = item["quantity"] * item["unit_price"]
            tax_rate = item.get("tax_rate") or Decimal("0.00")
            item["line_total"] = base + (base * tax_rate / Decimal("100"))
            InvoiceLineItem.objects.create(invoice=invoice, related_membership=membership, **item)
        invoice.recompute_totals()
        return invoice


def _next_invoice_number(organization):
    n = Invoice.objects.filter(organization=organization).count() + 1
    code = f"INV-{n:06d}"
    while Invoice.objects.filter(organization=organization, invoice_number=code).exists():
        n += 1
        code = f"INV-{n:06d}"
    return code
