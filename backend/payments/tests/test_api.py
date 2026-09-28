import hashlib
import hmac
import json
from decimal import Decimal

import pytest
from django.test import override_settings
from rest_framework import status

from accounts.tests.factories import OwnerFactory, UserFactory
from billing.models import Invoice
from billing.tests.factories import InvoiceFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from payments.models import Payment
from payments.providers import FakePaymentProvider
from payments.services import initiate_gateway_payment
from payments.tests.factories import SubscriptionFactory

pytestmark = pytest.mark.django_db


def test_cash_payment_and_tenant_isolation():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    member_a = MemberFactory(organization=owner_a.organization, home_branch=BranchFactory(organization=owner_a.organization))
    invoice = InvoiceFactory(member=member_a, organization=owner_a.organization, total=Decimal("2000.00"))

    paid = auth_client(owner_a).post(
        "/api/v1/payments/cash/",
        {"invoice_id": str(invoice.uuid), "amount": "2000.00", "method": "CASH", "idempotency_key": "cash-1"},
        format="json",
    )
    assert paid.status_code == status.HTTP_201_CREATED
    assert paid.data["data"]["status"] == Payment.Status.SUCCESSFUL

    invoice.refresh_from_db()
    assert invoice.status == Invoice.Status.PAID

    listed_b = auth_client(owner_b).get("/api/v1/payments/")
    assert listed_b.data["meta"]["total"] == 0


@override_settings(RAZORPAY_WEBHOOK_SECRET="whsec")
def test_razorpay_webhook_endpoint_is_idempotent():
    invoice = InvoiceFactory(total=Decimal("500.00"), status=Invoice.Status.ISSUED)
    payment = initiate_gateway_payment(
        invoice_id=invoice.id, amount=Decimal("500.00"), provider=FakePaymentProvider()
    )
    body_dict = {
        "id": "evt_api_1",
        "event": "payment.captured",
        "payload": {"payment": {"entity": {"order_id": payment.gateway_order_id}}},
    }
    raw = json.dumps(body_dict).encode("utf-8")
    signature = hmac.new(b"whsec", raw, hashlib.sha256).hexdigest()
    from rest_framework.test import APIClient

    client = APIClient()
    first = client.post(
        "/api/v1/payments/webhooks/razorpay/",
        data=raw,
        content_type="application/json",
        HTTP_X_RAZORPAY_SIGNATURE=signature,
    )
    assert first.status_code == 200
    second = client.post(
        "/api/v1/payments/webhooks/razorpay/",
        data=raw,
        content_type="application/json",
        HTTP_X_RAZORPAY_SIGNATURE=signature,
    )
    assert second.status_code == 200
    assert second.data["data"]["duplicate"] is True
    payment.refresh_from_db()
    assert payment.status == Payment.Status.SUCCESSFUL


def test_owner_lists_own_org_subscriptions_only():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    branch_a = BranchFactory(organization=owner_a.organization)
    member_a = MemberFactory(organization=owner_a.organization, home_branch=branch_a)
    own = SubscriptionFactory(member=member_a, organization=owner_a.organization)
    SubscriptionFactory()

    response = auth_client(owner_a).get("/api/v1/payments/subscriptions/")
    assert response.status_code == status.HTTP_200_OK
    ids = {row["id"] for row in response.data["data"]}
    assert ids == {str(own.uuid)}
    row = response.data["data"][0]
    assert row["member_id"] == str(member_a.uuid)
    assert row["plan_name"] == own.membership_plan.name
    assert row["status"] == own.status
    assert row["retry_count"] == 0
    assert row["gateway"] == "RAZORPAY"
    assert "next_billing_date" in row

    listed_b = auth_client(owner_b).get("/api/v1/payments/subscriptions/")
    assert listed_b.status_code == status.HTTP_200_OK
    assert listed_b.data["meta"]["total"] == 0


def test_member_cannot_see_other_member_subscriptions():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member_user = UserFactory(role="MEMBER", organization=owner.organization, home_branch=branch)
    other_user = UserFactory(role="MEMBER", organization=owner.organization, home_branch=branch)
    own_member = MemberFactory(organization=owner.organization, home_branch=branch, user=member_user)
    other_member = MemberFactory(organization=owner.organization, home_branch=branch, user=other_user)
    own = SubscriptionFactory(member=own_member, organization=owner.organization)
    SubscriptionFactory(member=other_member, organization=owner.organization)

    response = auth_client(member_user).get("/api/v1/payments/subscriptions/")
    assert response.status_code == status.HTTP_200_OK
    ids = {row["id"] for row in response.data["data"]}
    assert ids == {str(own.uuid)}


def test_trainer_cannot_list_subscriptions():
    owner = OwnerFactory()
    trainer = UserFactory(role="TRAINER", organization=owner.organization)
    response = auth_client(trainer).get("/api/v1/payments/subscriptions/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_member_can_initiate_own_invoice_via_fake_provider():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization)
    member_user = UserFactory(role="MEMBER", organization=owner.organization, home_branch=branch)
    other_user = UserFactory(role="MEMBER", organization=owner.organization, home_branch=branch)
    own_member = MemberFactory(organization=owner.organization, home_branch=branch, user=member_user)
    other_member = MemberFactory(organization=owner.organization, home_branch=branch, user=other_user)
    own_invoice = InvoiceFactory(
        member=own_member,
        organization=owner.organization,
        total=Decimal("1500.00"),
        status=Invoice.Status.ISSUED,
    )
    other_invoice = InvoiceFactory(
        member=other_member,
        organization=owner.organization,
        total=Decimal("900.00"),
        status=Invoice.Status.ISSUED,
    )

    own = auth_client(member_user).post(
        "/api/v1/payments/initiate/",
        {"invoice_id": str(own_invoice.uuid)},
        format="json",
    )
    assert own.status_code == status.HTTP_201_CREATED
    assert own.data["data"]["status"] == Payment.Status.INITIATED
    assert own.data["data"]["gateway_order_id"].startswith("order_fake_")

    foreign = auth_client(member_user).post(
        "/api/v1/payments/initiate/",
        {"invoice_id": str(other_invoice.uuid)},
        format="json",
    )
    assert foreign.status_code == status.HTTP_400_BAD_REQUEST


def test_subscription_list_has_no_charge_or_create_endpoint():
    owner = OwnerFactory()
    client = auth_client(owner)

    create = client.post("/api/v1/payments/subscriptions/", {}, format="json")
    assert create.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    charge = client.post("/api/v1/payments/subscriptions/charge/", {}, format="json")
    assert charge.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED)

    sub = SubscriptionFactory(
        member=MemberFactory(
            organization=owner.organization,
            home_branch=BranchFactory(organization=owner.organization),
        ),
        organization=owner.organization,
    )
    charge_detail = client.post(
        f"/api/v1/payments/subscriptions/{sub.uuid}/charge/",
        {},
        format="json",
    )
    assert charge_detail.status_code == status.HTTP_404_NOT_FOUND

    retry = client.post(
        f"/api/v1/payments/subscriptions/{sub.uuid}/retry/",
        {},
        format="json",
    )
    assert retry.status_code == status.HTTP_404_NOT_FOUND
