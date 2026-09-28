from django.contrib import admin

from .models import Payment, PaymentEvent, Refund, Subscription


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    readonly_fields = ["created_at", "processed_at"]


class PaymentEventInline(admin.TabularInline):
    model = PaymentEvent
    extra = 0
    readonly_fields = ["received_at", "processed_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "invoice", "amount", "method", "gateway", "status", "paid_at"]
    list_filter = ["status", "method", "gateway", "organization"]
    search_fields = ["gateway_payment_id", "gateway_order_id", "idempotency_key", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["invoice", "recorded_by"]
    inlines = [PaymentEventInline, RefundInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["member", "membership_plan", "status", "next_billing_date"]
    list_filter = ["status", "gateway", "organization"]
    autocomplete_fields = ["member", "membership_plan"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
