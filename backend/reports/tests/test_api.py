from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status

from accounts.tests.factories import OwnerFactory, UserFactory
from attendance.tests.factories import AttendanceFactory
from billing.models import Invoice
from billing.tests.factories import InvoiceFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from members.tests.factories import MemberFactory
from memberships.models import Membership
from memberships.tests.factories import MembershipFactory
from payments.models import Payment
from payments.tests.factories import PaymentFactory
from pt.tests.factories import PTPackageFactory, PTSessionFactory

pytestmark = pytest.mark.django_db

DASHBOARD_URL = "/api/v1/reports/dashboard/"
DASHBOARD_CSV_URL = "/api/v1/reports/dashboard.csv"
EXPIRED_MEMBERS_CSV_URL = "/api/v1/reports/expired-members.csv"


def _member_for(user):
    org = user.organization
    return MemberFactory(organization=org, home_branch=BranchFactory(organization=org))


def test_owner_dashboard_returns_envelope():
    owner = OwnerFactory()
    member = _member_for(owner)
    InvoiceFactory(member=member, organization=owner.organization, total=Decimal("500.00"), status=Invoice.Status.ISSUED)
    PaymentFactory(
        invoice=InvoiceFactory(
            member=member,
            organization=owner.organization,
            total=Decimal("1000.00"),
            status=Invoice.Status.PAID,
        ),
        organization=owner.organization,
        amount=Decimal("1000.00"),
        status=Payment.Status.SUCCESSFUL,
    )
    MembershipFactory(member=member, organization=owner.organization, status=Membership.Status.ACTIVE)
    AttendanceFactory(member=member, organization=owner.organization, checkin_at=timezone.now())
    package = PTPackageFactory(member=member, organization=owner.organization, sessions_purchased=8, sessions_consumed=2)
    PTSessionFactory(
        package=package,
        member=member,
        trainer=package.trainer,
        organization=owner.organization,
    )

    response = auth_client(owner).get(DASHBOARD_URL)

    assert response.status_code == status.HTTP_200_OK
    payload = response.data["data"]
    assert set(payload) == {"revenue", "membership", "attendance", "pt"}
    assert Decimal(payload["revenue"]["today_collection"]) == Decimal("1000.00")
    assert "by_branch" in payload["revenue"]
    by_branch = payload["revenue"]["by_branch"]
    assert {row["branch_id"] for row in by_branch} >= {str(member.home_branch.uuid)}
    home_row = next(row for row in by_branch if row["branch_id"] == str(member.home_branch.uuid))
    assert home_row["branch_name"] == member.home_branch.name
    assert Decimal(home_row["monthly_collection"]) == Decimal("1000.00")
    assert payload["membership"]["active"] == 1
    assert payload["attendance"]["today_checkins"] == 1
    assert payload["pt"]["remaining_package_sessions"] == 6


def test_staff_cannot_access_owner_dashboard():
    owner = OwnerFactory()
    staff = UserFactory(role="STAFF_ADMIN", organization=owner.organization)
    response = auth_client(staff).get(DASHBOARD_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_owner_dashboard_csv_returns_text_csv():
    owner = OwnerFactory()
    member = _member_for(owner)
    PaymentFactory(
        invoice=InvoiceFactory(
            member=member,
            organization=owner.organization,
            total=Decimal("1000.00"),
            status=Invoice.Status.PAID,
        ),
        organization=owner.organization,
        amount=Decimal("1000.00"),
        status=Payment.Status.SUCCESSFUL,
    )

    response = auth_client(owner).get(DASHBOARD_CSV_URL)

    assert response.status_code == status.HTTP_200_OK
    assert "text/csv" in response["Content-Type"]
    body = response.content.decode()
    assert "section,metric,value" in body
    assert "today_collection" in body
    assert "1000.00" in body


def test_staff_cannot_access_owner_dashboard_csv():
    owner = OwnerFactory()
    staff = UserFactory(role="STAFF_ADMIN", organization=owner.organization)
    response = auth_client(staff).get(DASHBOARD_CSV_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_owner_dashboard_csv_excludes_other_organization():
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

    response = auth_client(owner_a).get(DASHBOARD_CSV_URL, {"organization": owner_b.organization_id})

    assert response.status_code == status.HTTP_200_OK
    assert "text/csv" in response["Content-Type"]
    body = response.content.decode()
    assert "1000.00" in body
    assert "99999.00" not in body


def test_owner_expired_members_csv_includes_own_org_not_other():
    owner_a = OwnerFactory()
    owner_b = OwnerFactory()
    member_a = MemberFactory(
        organization=owner_a.organization,
        home_branch=BranchFactory(organization=owner_a.organization),
        member_code="EXPA-001",
        full_name="OrgA Expired Member",
        phone="+919111100001",
    )
    member_b = MemberFactory(
        organization=owner_b.organization,
        home_branch=BranchFactory(organization=owner_b.organization),
        member_code="EXPB-001",
        full_name="OrgB Expired Member",
        phone="+919111100002",
    )
    active_a = MemberFactory(
        organization=owner_a.organization,
        home_branch=BranchFactory(organization=owner_a.organization),
        member_code="ACTA-001",
        full_name="OrgA Active Member",
        phone="+919111100003",
    )
    MembershipFactory(
        member=member_a,
        organization=owner_a.organization,
        status=Membership.Status.EXPIRED,
        end_date=timezone.localdate(),
    )
    MembershipFactory(
        member=member_b,
        organization=owner_b.organization,
        status=Membership.Status.EXPIRED,
        end_date=timezone.localdate(),
    )
    MembershipFactory(
        member=active_a,
        organization=owner_a.organization,
        status=Membership.Status.ACTIVE,
    )

    response = auth_client(owner_a).get(EXPIRED_MEMBERS_CSV_URL, {"organization": owner_b.organization_id})

    assert response.status_code == status.HTTP_200_OK
    assert "text/csv" in response["Content-Type"]
    body = response.content.decode()
    header = body.splitlines()[0]
    assert header == "member_id,member_code,full_name,phone,membership_end_date,membership_status"
    assert str(member_a.uuid) in body
    assert "EXPA-001" in body
    assert "OrgA Expired Member" in body
    assert "+919111100001" in body
    assert "EXPIRED" in body
    assert str(member_b.uuid) not in body
    assert "EXPB-001" not in body
    assert "OrgB Expired Member" not in body
    assert "+919111100002" not in body
    assert str(active_a.uuid) not in body
    assert "ACTA-001" not in body


def test_staff_cannot_access_expired_members_csv():
    owner = OwnerFactory()
    staff = UserFactory(role="STAFF_ADMIN", organization=owner.organization)
    response = auth_client(staff).get(EXPIRED_MEMBERS_CSV_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN
