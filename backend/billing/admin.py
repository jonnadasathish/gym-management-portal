from django.contrib import admin

from .models import Invoice, InvoiceLineItem


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "member", "status", "total", "issue_date"]
    list_filter = ["status", "organization"]
    search_fields = ["invoice_number", "member__full_name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["member", "created_by"]
    inlines = [InvoiceLineItemInline]
