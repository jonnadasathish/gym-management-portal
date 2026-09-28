"""Tenant isolation for owner-dashboard aggregations (AGENTS.md §16.4)."""

from decimal import Decimal

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from billing.models import Invoice
from billing.tests.factories import InvoiceFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from payments.models import Payment
from payments.tests.factories import PaymentFactory

pytestmark = pytest.mark.django_db

DASHBOARD_URL = "/api/v1/reports/dashboard/"


def test_owner_dashboard_excludes_other_organization():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    member_a = MemberFactory(
        organization=owner_a.organization,
        home_branch=BranchFactory(organization=owner_a.organization),
    )
    member_b = MemberFactory(
        organization=owner_b.organization,
        home_branch=BranchFactory(organization=owner_b.organization),
    )
    PaymentFactory(
        invoice=InvoiceFactory(
            member=member_a,
            organization=owner_a.organization,
            total=Decimal("1000.00"),
            status=Invoice.Status.PAID,
        ),
        organization=owner_a.organization,
        amount=Decimal("1000.00"),
        status=Payment.Status.SUCCESSFUL,
    )
    PaymentFactory(
        invoice=InvoiceFactory(
            member=member_b,
            organization=owner_b.organization,
            total=Decimal("99999.00"),
            status=Invoice.Status.PAID,
        ),
        organization=owner_b.organization,
        amount=Decimal("99999.00"),
        status=Payment.Status.SUCCESSFUL,
    )
    InvoiceFactory(
        member=member_a,
        organization=owner_a.organization,
        total=Decimal("250.00"),
        status=Invoice.Status.ISSUED,
    )
    InvoiceFactory(
        member=member_b,
        organization=owner_b.organization,
        total=Decimal("88888.00"),
        status=Invoice.Status.ISSUED,
    )

    response = auth_client(owner_a).get(DASHBOARD_URL, {"organization": owner_b.organization_id})

    assert response.status_code == status.HTTP_200_OK
    revenue = response.data["data"]["revenue"]
    assert Decimal(revenue["today_collection"]) == Decimal("1000.00")
    assert Decimal(revenue["pending_dues"]) == Decimal("250.00")
    assert Decimal(revenue["monthly_collection"]) == Decimal("1000.00")
    by_branch_ids = {row["branch_id"] for row in revenue["by_branch"]}
    assert str(member_a.home_branch.uuid) in by_branch_ids
    assert str(member_b.home_branch.uuid) not in by_branch_ids
    home_row = next(row for row in revenue["by_branch"] if row["branch_id"] == str(member_a.home_branch.uuid))
    assert Decimal(home_row["monthly_collection"]) == Decimal("1000.00")
