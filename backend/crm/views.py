from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.api import STAFF_AND_TRAINER, TenantScopedAPIMixin, authorized_branch_ids
from core.permissions import HasRole, IsOrgMember
from crm.models import Lead, LeadActivity
from crm.serializers import LeadActivitySerializer, LeadActivityWriteSerializer, LeadSerializer
from crm.services import CRMStateError, convert_lead


class LeadViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = Lead.objects.select_related("branch", "interested_plan", "assigned_staff", "converted_member")
    serializer_class = LeadSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        return [IsAuthenticated(), IsOrgMember(), HasRole(*STAFF_AND_TRAINER)]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "TRAINER":
            return qs.filter(assigned_staff=user)
        return qs.filter(branch_id__in=authorized_branch_ids(user) or [-1])

    @action(detail=True, methods=["post"])
    def convert(self, request, uuid=None):
        lead = self.get_object()
        try:
            lead, _member = convert_lead(lead_id=lead.id)
        except CRMStateError as exc:
            return Response(
                {"error": {"code": exc.code, "message": str(exc)}},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(LeadSerializer(lead, context={"request": request}).data)

    @action(detail=True, methods=["get", "post"], url_path="activities")
    def activities(self, request, uuid=None):
        lead = self.get_object()
        if request.method == "GET":
            qs = lead.activities.select_related("created_by").all()
            return Response(LeadActivitySerializer(qs, many=True).data)
        serializer = LeadActivityWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity = LeadActivity(
            organization=lead.organization,
            lead=lead,
            activity_type=serializer.validated_data["activity_type"],
            notes=serializer.validated_data.get("notes", ""),
            created_by=request.user,
        )
        activity.full_clean()
        activity.save()
        return Response(LeadActivitySerializer(activity).data, status=status.HTTP_201_CREATED)
