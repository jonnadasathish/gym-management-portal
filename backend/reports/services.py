"""Owner-dashboard aggregations derived from authoritative domain models.

Do not persist report totals. Money comes from `payments.Payment.amount`
(SUCCESSFUL) and `payments.Refund.amount` (PROCESSED); dues from
`billing.Invoice.total` where status is not PAID.
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db.models import CharField, DateField, DecimalField, F, IntegerField, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from attendance.models import Attendance
from billing.models import Invoice
from branches.models import Branch
from members.models import Member
from memberships.models import Membership
from payments.models import Payment
from pt.models import PTPackage, PTSession

IST = ZoneInfo("Asia/Kolkata")
ZERO = Decimal("0.00")
MONEY = DecimalField(max_digits=12, decimal_places=2)


def _money(value):
    if value is None:
        return ZERO
    return Decimal(value).quantize(Decimal("0.01"))


def _start_of_day(day, tz):
    return timezone.make_aware(datetime.combine(day, time.min), timezone=tz)


def _month_bounds(today):
    month_start_date = today.replace(day=1)
    if month_start_date.month == 12:
        next_month_date = date(month_start_date.year + 1, 1, 1)
    else:
        next_month_date = date(month_start_date.year, month_start_date.month + 1, 1)
    return month_start_date, next_month_date


def _sum_money(queryset, field="amount"):
    return queryset.aggregate(total=Coalesce(Sum(field), Value(ZERO, output_field=MONEY), output_field=MONEY))["total"]


def _revenue_by_branch(organization, successful_month):
    """SUCCESSFUL payment totals keyed by invoice.member.home_branch.

    Every organization branch is included, including those with zero
    collection this month. `successful_month` must already be filtered to
    SUCCESSFUL payments in the same bounds as `monthly_collection`.
    """

    totals = {
        row["invoice__member__home_branch_id"]: row["total"]
        for row in successful_month.values("invoice__member__home_branch_id").annotate(
            total=Coalesce(Sum("amount"), Value(ZERO, output_field=MONEY), output_field=MONEY)
        )
    }
    return [
        {
            "branch_id": str(branch.uuid),
            "branch_name": branch.name,
            "monthly_collection": _money(totals.get(branch.id, ZERO)),
        }
        for branch in Branch.objects.for_organization(organization).order_by("name")
    ]


def _refunds_month(organization, month_start, next_month_start):
    try:
        from payments.models import Refund
    except ImportError:
        return ZERO
    return _sum_money(
        Refund.objects.filter(
            payment__organization=organization,
            status=Refund.Status.PROCESSED,
            created_at__gte=month_start,
            created_at__lt=next_month_start,
        )
    )


def owner_dashboard(organization, *, today=None) -> dict:
    """Return owner-dashboard metrics scoped to `organization` only.

    Date boundaries for 'today' / the calendar month use Asia/Kolkata via
    `django.utils.timezone` (`today=None` → `timezone.localdate`).
    """

    tz = IST
    if today is None:
        today = timezone.localdate(timezone=tz)

    day_start = _start_of_day(today, tz)
    day_end = day_start + timedelta(days=1)
    month_start_date, next_month_date = _month_bounds(today)
    month_start = _start_of_day(month_start_date, tz)
    next_month_start = _start_of_day(next_month_date, tz)

    successful = Payment.objects.for_organization(organization).filter(status=Payment.Status.SUCCESSFUL)
    today_collection = _sum_money(successful.filter(created_at__gte=day_start, created_at__lt=day_end))
    successful_month = successful.filter(created_at__gte=month_start, created_at__lt=next_month_start)
    monthly_collection = _sum_money(successful_month)
    by_branch = _revenue_by_branch(organization, successful_month)

    pending_dues = _sum_money(
        Invoice.objects.for_organization(organization).exclude(status=Invoice.Status.PAID),
        field="total",
    )
    refunds_month = _refunds_month(organization, month_start, next_month_start)

    memberships = Membership.objects.for_organization(organization)
    active_qs = memberships.filter(status=Membership.Status.ACTIVE)

    remaining_package_sessions = (
        PTPackage.objects.for_organization(organization).aggregate(
            total=Coalesce(
                Sum(F("sessions_purchased") - F("sessions_consumed")),
                Value(0),
                output_field=IntegerField(),
            )
        )["total"]
        or 0
    )

    sessions = PTSession.objects.for_organization(organization)

    return {
        "revenue": {
            "today_collection": _money(today_collection),
            "monthly_collection": _money(monthly_collection),
            "pending_dues": _money(pending_dues),
            "refunds_month": _money(refunds_month),
            "by_branch": by_branch,
        },
        "membership": {
            "active": active_qs.count(),
            "expired": memberships.filter(status=Membership.Status.EXPIRED).count(),
            "expiring_7": active_qs.filter(end_date__gte=today, end_date__lte=today + timedelta(days=7)).count(),
            "expiring_30": active_qs.filter(end_date__gte=today, end_date__lte=today + timedelta(days=30)).count(),
            "new_month": memberships.filter(start_date__gte=month_start_date, start_date__lt=next_month_date).count(),
            "cancelled": memberships.filter(status=Membership.Status.CANCELLED).count(),
            "frozen": memberships.filter(status=Membership.Status.FROZEN).count(),
        },
        "attendance": {
            "today_checkins": Attendance.objects.for_organization(organization)
            .filter(checkin_at__gte=day_start, checkin_at__lt=day_end)
            .count(),
        },
        "pt": {
            "scheduled_sessions": sessions.filter(status=PTSession.Status.SCHEDULED).count(),
            "completed_sessions": sessions.filter(status=PTSession.Status.COMPLETED).count(),
            "remaining_package_sessions": int(remaining_package_sessions),
        },
    }


def expired_members(organization):
    """Distinct members whose *latest* membership is EXPIRED.

    Authoritative source is `Membership.status` (not `Member.status`, which
    is a derived display field). Latest membership is the one with the
    newest `start_date` (then `id`) for that member in this organization.
    """

    latest = (
        Membership.objects.for_organization(organization)
        .filter(member_id=OuterRef("pk"))
        .order_by("-start_date", "-id")
    )
    return (
        Member.objects.for_organization(organization)
        .alive()
        .annotate(
            membership_end_date=Subquery(latest.values("end_date")[:1], output_field=DateField()),
            membership_status=Subquery(latest.values("status")[:1], output_field=CharField(max_length=20)),
        )
        .filter(membership_status=Membership.Status.EXPIRED)
        .order_by("full_name", "member_code")
    )
