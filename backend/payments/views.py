import json

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api import FRONT_DESK_ROLES, TenantScopedAPIMixin, authorized_branch_ids
from core.exceptions import ConflictError
from core.permissions import HasRole, IsOrgMember
from payments.models import Payment, Subscription
from payments.providers import FakePaymentProvider, RazorpayProvider
from payments.serializers import (
    CashPaymentSerializer,
    InitiatePaymentSerializer,
    PaymentSerializer,
    SubscriptionSerializer,
)
from payments.services import (
    DuplicateWebhookEvent,
    PaymentStateError,
    handle_webhook_event,
    initiate_gateway_payment,
    record_cash_payment,
)

_EVENT_STATUS = {
    "payment.captured": Payment.Status.SUCCESSFUL,
    "order.paid": Payment.Status.SUCCESSFUL,
    "payment.failed": Payment.Status.FAILED,
}


class PaymentViewSet(TenantScopedAPIMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("invoice")
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.action == "cash":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        if self.action == "initiate":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES, "MEMBER")]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "MEMBER":
            return qs.filter(invoice__member__user=user)
        if user.role == "TRAINER":
            return qs.filter(invoice__member__assigned_trainer=user)
        return qs.filter(invoice__member__home_branch_id__in=authorized_branch_ids(user) or [-1])

    @action(detail=False, methods=["post"])
    def cash(self, request):
        serializer = CashPaymentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        invoice = serializer.validated_data["invoice_id"]
        idempotency_key = serializer.validated_data.get("idempotency_key") or request.headers.get("Idempotency-Key")
        payment = record_cash_payment(
            invoice_id=invoice.id,
            amount=serializer.validated_data["amount"],
            method=serializer.validated_data["method"],
            recorded_by=request.user,
            idempotency_key=idempotency_key or None,
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def initiate(self, request):
        """Create a PENDING/INITIATED gateway payment. Uses FakePaymentProvider
        unless Razorpay keys are configured — live HTTPS remains unverified.
        """

        serializer = InitiatePaymentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        invoice = serializer.validated_data["invoice_id"]
        amount = serializer.validated_data.get("amount") or invoice.total
        key_id = getattr(settings, "RAZORPAY_KEY_ID", "") or ""
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "") or ""
        if key_id and key_secret:
            provider = RazorpayProvider(key_id=key_id, key_secret=key_secret)
        else:
            provider = FakePaymentProvider()
        payment = initiate_gateway_payment(invoice_id=invoice.id, amount=amount, provider=provider)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class SubscriptionViewSet(TenantScopedAPIMixin, viewsets.ReadOnlyModelViewSet):
    """REQ-034 visibility only. Charge, retry, and mandate capture are out of scope."""

    queryset = Subscription.objects.select_related("member", "membership_plan")
    serializer_class = SubscriptionSerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = [IsAuthenticated, IsOrgMember, HasRole(*FRONT_DESK_ROLES, "MEMBER")]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            scoped = qs
        elif user.role == "MEMBER":
            scoped = qs.filter(member__user=user)
        else:
            scoped = qs.filter(member__home_branch_id__in=authorized_branch_ids(user) or [-1])
        return scoped.select_related("member", "membership_plan").order_by("-created_at")


class RazorpayWebhookView(APIView):
    """Public webhook — authenticity is the HMAC, not a user JWT (REQ-035)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        raw = request.body
        signature = request.headers.get("X-Razorpay-Signature", "")
        secret = getattr(settings, "RAZORPAY_WEBHOOK_SECRET", "") or ""
        provider = RazorpayProvider(key_id=getattr(settings, "RAZORPAY_KEY_ID", ""), key_secret="")

        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Invalid JSON payload."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_type = payload.get("event") or ""
        new_status = _EVENT_STATUS.get(event_type)
        if not new_status:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Unsupported webhook event."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entity = ((payload.get("payload") or {}).get("payment") or {}).get("entity") or {}
        gateway_order_id = entity.get("order_id") or payload.get("gateway_order_id") or ""
        gateway_event_id = payload.get("id") or entity.get("id") or ""
        if not gateway_order_id or not gateway_event_id:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Missing gateway identifiers."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = handle_webhook_event(
                provider=provider,
                payload_body=raw,
                signature=signature,
                webhook_secret=secret,
                gateway_event_id=str(gateway_event_id),
                event_type=event_type,
                gateway_order_id=gateway_order_id,
                new_status=new_status,
                raw_payload=payload,
            )
        except PaymentStateError as exc:
            raise ConflictError(detail=str(exc))
        except DuplicateWebhookEvent:
            return Response({"data": {"duplicate": True}}, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "No payment matches this gateway order."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(PaymentSerializer(payment).data)
