"""Invoice models. See PROJECT_CONTEXT.md §27.A, §21-22, REQ-030..REQ-037.

GST FIELD CAVEAT (OQ-004, still OPEN): `gst_details` is a flexible JSON
snapshot rather than named columns, deliberately, because the PRD is
explicit that exact GST invoice field requirements must be confirmed with
finance/legal (AGENTS.md §22). Do not treat any specific key inside it as
an approved legal requirement.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TenantScopedModel


class Invoice(TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ISSUED = "ISSUED", "Issued"
        PAID = "PAID", "Paid"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially paid"
        VOID = "VOID", "Void"

    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="invoices")
    invoice_number = models.CharField(max_length=50)
    issue_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    gst_details = models.JSONField(default=dict, blank=True, help_text="Flexible snapshot — see OQ-004.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices_created"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "invoice_number"], name="unique_invoice_number_per_org"),
        ]
        indexes = [models.Index(fields=["organization", "status"])]
        ordering = ["-issue_date"]

    def __str__(self):
        return f"{self.invoice_number} ({self.status})"

    def clean(self):
        super().clean()
        if self.member_id and self.organization_id and self.member.organization_id != self.organization_id:
            raise ValidationError("Invoice.organization must match member.organization.")

    def recompute_totals(self, *, save=True):
        """Derive subtotal/tax/total from line items — never hand-edited
        independently (single source of truth for the arithmetic)."""

        line_items = self.line_items.all()
        subtotal = sum((item.quantity * item.unit_price for item in line_items), Decimal("0.00"))
        tax = sum((item.line_total - (item.quantity * item.unit_price) for item in line_items), Decimal("0.00"))
        self.subtotal = subtotal
        self.tax = tax
        self.total = subtotal + tax - self.discount
        if save:
            self.save(update_fields=["subtotal", "tax", "total", "updated_at"])


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    related_membership = models.ForeignKey(
        "memberships.Membership", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoice_line_items"
    )
    related_pt_package = models.ForeignKey(
        "pt.PTPackage", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoice_line_items"
    )

    def __str__(self):
        return f"{self.description} x{self.quantity}"

    def save(self, *args, **kwargs):
        if self.line_total is None:
            base = self.quantity * self.unit_price
            self.line_total = base + (base * self.tax_rate / Decimal("100"))
        super().save(*args, **kwargs)
