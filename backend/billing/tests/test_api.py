from decimal import Decimal

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory

pytestmark = pytest.mark.django_db


def test_owner_creates_invoice():
    owner = OwnerFactory()
    member = MemberFactory(
        organization=owner.organization,
        home_branch=BranchFactory(organization=owner.organization),
    )
    response = auth_client(owner).post(
        "/api/v1/billing/",
        {
            "member_id": str(member.uuid),
            "issue_date": "2026-09-28",
            "discount": "0.00",
            "line_items": [
                {
                    "description": "Monthly membership",
                    "quantity": "1.00",
                    "unit_price": "2000.00",
                    "tax_rate": "0.00",
                }
            ],
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["data"]["total"] == "2000.00"
    assert response.data["data"]["status"] == "ISSUED"
