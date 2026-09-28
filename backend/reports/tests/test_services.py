from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from attendance.tests.factories import AttendanceFactory
from billing.models import Invoice
from billing.tests.factories import InvoiceFactory
from branches.models import Branch
from branches.tests.factories import BranchFactory
from members.tests.factories import MemberFactory
from memberships.models import Membership
from memberships.tests.factories import MembershipFactory
from organizations.tests.factories import OrganizationFactory
from payments.models import Payment, Refund
from payments.tests.factories import PaymentFactory
from pt.models import PTSession
from pt.tests.factories import PTPackageFactory, PTSessionFactory
from reports.services import IST, owner_dashboard

pytestmark = pytest.mark.django_db

TODAY = date(2026, 9, 28)


def _ist(day, hour=10):
    return timezone.make_aware(datetime.combine(day, time(hour=hour)), timezone=IST)


def _set_created_at(instance, when):
    type(instance).objects.filter(pk=instance.pk).update(created_at=when)
    instance.refresh_from_db()


def _member(org):
    return MemberFactory(organization=org, home_branch=BranchFactory(organization=org))


def _payment(member, amount, status, created_at, invoice_status=Invoice.Status.PAID):
    invoice = InvoiceFactory(
        member=member,
        organization=member.organization,
        total=amount,
        status=invoice_status,
    )
    payment = PaymentFactory(
        invoice=invoice,
        organization=member.organization,
        amount=amount,
        status=status,
    )
    _set_created_at(payment, created_at)
    return payment


def test_owner_dashboard_counts_only_requested_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    member_a = _member(org_a)
    member_b = _member(org_b)

    _payment(member_a, Decimal("1000.00"), Payment.Status.SUCCESSFUL, _ist(TODAY))
    _payment(member_a, Decimal("2000.00"), Payment.Status.SUCCESSFUL, _ist(date(2026, 9, 10)))
    _payment(member_a, Decimal("5000.00"), Payment.Status.SUCCESSFUL, _ist(date(2026, 8, 15)))
    _payment(member_a, Decimal("3000.00"), Payment.Status.FAILED, _ist(TODAY))
    _payment(member_b, Decimal("99999.00"), Payment.Status.SUCCESSFUL, _ist(TODAY))

    InvoiceFactory(member=member_a, organization=org_a, total=Decimal("750.00"), status=Invoice.Status.ISSUED)
    InvoiceFactory(member=member_b, organization=org_b, total=Decimal("50000.00"), status=Invoice.Status.ISSUED)

    refund_payment = _payment(member_a, Decimal("400.00"), Payment.Status.SUCCESSFUL, _ist(TODAY))
    refund = Refund.objects.create(
        payment=refund_payment,
        amount=Decimal("50.00"),
        reason="Adjustment",
        status=Refund.Status.PROCESSED,
        processed_at=_ist(TODAY),
    )
    _set_created_at(refund, _ist(TODAY))
    Refund.objects.create(
        payment=refund_payment,
        amount=Decimal("999.00"),
        reason="Pending",
        status=Refund.Status.PENDING,
    )
    other_refund_payment = _payment(member_b, Decimal("800.00"), Payment.Status.SUCCESSFUL, _ist(TODAY))
    Refund.objects.create(
        payment=other_refund_payment,
        amount=Decimal("5000.00"),
        reason="Other org",
        status=Refund.Status.PROCESSED,
        processed_at=_ist(TODAY),
    )

    MembershipFactory(
        member=member_a,
        organization=org_a,
        start_date=TODAY,
        end_date=TODAY + timedelta(days=5),
        status=Membership.Status.ACTIVE,
    )
    MembershipFactory(
        member=_member(org_a),
        organization=org_a,
        start_date=date(2026, 8, 1),
        end_date=TODAY + timedelta(days=20),
        status=Membership.Status.ACTIVE,
    )
    MembershipFactory(
        member=_member(org_a),
        organization=org_a,
        start_date=date(2026, 8, 1),
        end_date=TODAY + timedelta(days=90),
        status=Membership.Status.ACTIVE,
    )
    MembershipFactory(
        member=_member(org_a),
        organization=org_a,
        start_date=date(2026, 6, 1),
        end_date=date(2026, 9, 1),
        status=Membership.Status.EXPIRED,
    )
    MembershipFactory(
        member=_member(org_a),
        organization=org_a,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 10, 1),
        status=Membership.Status.CANCELLED,
    )
    MembershipFactory(
        member=_member(org_a),
        organization=org_a,
        start_date=date(2026, 8, 1),
        end_date=date(2026, 11, 1),
        status=Membership.Status.FROZEN,
    )
    MembershipFactory(
        member=member_b,
        organization=org_b,
        start_date=TODAY,
        end_date=TODAY + timedelta(days=3),
        status=Membership.Status.ACTIVE,
    )
    MembershipFactory(
        member=_member(org_b),
        organization=org_b,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 2, 1),
        status=Membership.Status.EXPIRED,
    )
    MembershipFactory(
        member=_member(org_b),
        organization=org_b,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 1),
        status=Membership.Status.CANCELLED,
    )
    MembershipFactory(
        member=_member(org_b),
        organization=org_b,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 1),
        status=Membership.Status.FROZEN,
    )

    AttendanceFactory(member=member_a, organization=org_a, checkin_at=_ist(TODAY, 8))
    AttendanceFactory(member=member_a, organization=org_a, checkin_at=_ist(TODAY, 18))
    AttendanceFactory(member=member_a, organization=org_a, checkin_at=_ist(date(2026, 9, 27), 20))
    AttendanceFactory(member=member_b, organization=org_b, checkin_at=_ist(TODAY, 9))
    AttendanceFactory(member=member_b, organization=org_b, checkin_at=_ist(TODAY, 11))

    package_a = PTPackageFactory(member=member_a, organization=org_a, sessions_purchased=10, sessions_consumed=3)
    PTPackageFactory(member=_member(org_a), organization=org_a, sessions_purchased=5, sessions_consumed=1)
    PTSessionFactory(
        package=package_a,
        member=member_a,
        trainer=package_a.trainer,
        organization=org_a,
        status=PTSession.Status.SCHEDULED,
    )
    PTSessionFactory(
        package=package_a,
        member=member_a,
        trainer=package_a.trainer,
        organization=org_a,
        status=PTSession.Status.SCHEDULED,
    )
    PTSessionFactory(
        package=package_a,
        member=member_a,
        trainer=package_a.trainer,
        organization=org_a,
        status=PTSession.Status.COMPLETED,
    )
    PTSessionFactory(
        package=package_a,
        member=member_a,
        trainer=package_a.trainer,
        organization=org_a,
        status=PTSession.Status.CANCELLED,
    )
    package_b = PTPackageFactory(member=member_b, organization=org_b, sessions_purchased=100, sessions_consumed=0)
    PTSessionFactory(
        package=package_b,
        member=member_b,
        trainer=package_b.trainer,
        organization=org_b,
        status=PTSession.Status.SCHEDULED,
    )
    PTSessionFactory(
        package=package_b,
        member=member_b,
        trainer=package_b.trainer,
        organization=org_b,
        status=PTSession.Status.COMPLETED,
    )

    result = owner_dashboard(org_a, today=TODAY)

    assert result["revenue"]["today_collection"] == Decimal("1400.00")
    assert result["revenue"]["monthly_collection"] == Decimal("3400.00")
    assert result["revenue"]["pending_dues"] == Decimal("750.00")
    assert result["revenue"]["refunds_month"] == Decimal("50.00")
    by_branch = result["revenue"]["by_branch"]
    assert {row["branch_id"] for row in by_branch} == {
        str(branch.uuid) for branch in Branch.objects.for_organization(org_a)
    }
    assert sum((row["monthly_collection"] for row in by_branch), Decimal("0.00")) == Decimal("3400.00")
    home_row = next(row for row in by_branch if row["branch_id"] == str(member_a.home_branch.uuid))
    assert home_row["branch_name"] == member_a.home_branch.name
    assert home_row["monthly_collection"] == Decimal("3400.00")
    assert str(member_b.home_branch.uuid) not in {row["branch_id"] for row in by_branch}
    assert result["membership"]["active"] == 3
    assert result["membership"]["expired"] == 1
    assert result["membership"]["expiring_7"] == 1
    assert result["membership"]["expiring_30"] == 2
    assert result["membership"]["new_month"] == 1
    assert result["membership"]["cancelled"] == 1
    assert result["membership"]["frozen"] == 1
    assert result["attendance"]["today_checkins"] == 2
    assert result["pt"]["scheduled_sessions"] == 2
    assert result["pt"]["completed_sessions"] == 1
    assert result["pt"]["remaining_package_sessions"] == 11


def test_owner_dashboard_revenue_by_branch_includes_zeros_and_sums_home_branch():
    org = OrganizationFactory()
    branch_a = BranchFactory(organization=org, name="Alpha")
    branch_b = BranchFactory(organization=org, name="Beta")
    branch_empty = BranchFactory(organization=org, name="Zulu")
    other = OrganizationFactory()
    other_branch = BranchFactory(organization=other, name="Other Gym")

    member_a = MemberFactory(organization=org, home_branch=branch_a)
    member_b = MemberFactory(organization=org, home_branch=branch_b)
    MemberFactory(organization=other, home_branch=other_branch)

    _payment(member_a, Decimal("1200.00"), Payment.Status.SUCCESSFUL, _ist(TODAY))
    _payment(member_a, Decimal("300.00"), Payment.Status.SUCCESSFUL, _ist(date(2026, 9, 5)))
    _payment(member_a, Decimal("999.00"), Payment.Status.FAILED, _ist(TODAY))
    _payment(member_a, Decimal("5000.00"), Payment.Status.SUCCESSFUL, _ist(date(2026, 8, 20)))
    _payment(member_b, Decimal("400.00"), Payment.Status.SUCCESSFUL, _ist(date(2026, 9, 12)))
    _payment(
        MemberFactory(organization=other, home_branch=other_branch),
        Decimal("88888.00"),
        Payment.Status.SUCCESSFUL,
        _ist(TODAY),
    )

    result = owner_dashboard(org, today=TODAY)
    by_branch = result["revenue"]["by_branch"]

    assert [row["branch_name"] for row in by_branch] == ["Alpha", "Beta", "Zulu"]
    assert by_branch[0] == {
        "branch_id": str(branch_a.uuid),
        "branch_name": "Alpha",
        "monthly_collection": Decimal("1500.00"),
    }
    assert by_branch[1] == {
        "branch_id": str(branch_b.uuid),
        "branch_name": "Beta",
        "monthly_collection": Decimal("400.00"),
    }
    assert by_branch[2] == {
        "branch_id": str(branch_empty.uuid),
        "branch_name": "Zulu",
        "monthly_collection": Decimal("0.00"),
    }
    assert str(other_branch.uuid) not in {row["branch_id"] for row in by_branch}
    assert result["revenue"]["monthly_collection"] == Decimal("1900.00")
