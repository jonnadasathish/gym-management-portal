import csv
import io

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api import EnvelopeMixin
from core.permissions import HasRole, IsOrgMember
from reports.serializers import OwnerDashboardSerializer
from reports.services import expired_members, owner_dashboard


class OwnerDashboardView(EnvelopeMixin, APIView):
    """GET owner dashboard. Organization is always `request.user.organization`."""

    permission_classes = [IsAuthenticated, IsOrgMember, HasRole("OWNER")]

    def get(self, request):
        payload = owner_dashboard(request.user.organization)
        return Response(OwnerDashboardSerializer(payload).data)


class OwnerDashboardCsvView(APIView):
    """GET owner dashboard as CSV. Same metrics as `owner_dashboard()` — no shadow totals.

    Returns Django `HttpResponse` (not DRF `Response`) so JSONRenderer / EnvelopeMixin
    cannot wrap the body. Failures still go through the JSON error envelope.
    """

    permission_classes = [IsAuthenticated, IsOrgMember, HasRole("OWNER")]

    def get(self, request):
        payload = owner_dashboard(request.user.organization)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["section", "metric", "value"])
        for section, metrics in payload.items():
            for metric, value in metrics.items():
                if isinstance(value, list):
                    for item in value:
                        writer.writerow(
                            [
                                section,
                                f"{metric}:{item.get('branch_name', '')}",
                                item.get("monthly_collection", ""),
                            ]
                        )
                else:
                    writer.writerow([section, metric, value])
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="dashboard.csv"'
        return response


class OwnerExpiredMembersCsvView(APIView):
    """GET expired members as CSV. Organization is always `request.user.organization`.

    One row per distinct member whose latest membership is EXPIRED.
    Columns come from Member + Membership — no shadow calculation.
    """

    permission_classes = [IsAuthenticated, IsOrgMember, HasRole("OWNER")]

    def get(self, request):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["member_id", "member_code", "full_name", "phone", "membership_end_date", "membership_status"]
        )
        for member in expired_members(request.user.organization):
            end_date = member.membership_end_date
            writer.writerow(
                [
                    str(member.uuid),
                    member.member_code,
                    member.full_name,
                    member.phone,
                    end_date.isoformat() if end_date else "",
                    member.membership_status,
                ]
            )
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="expired-members.csv"'
        return response
