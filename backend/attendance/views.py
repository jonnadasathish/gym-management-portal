from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer, CheckInSerializer
from attendance.services import AttendanceEligibilityError, check_in
from core.api import FRONT_DESK_ROLES, TenantScopedAPIMixin, authorized_branch_ids, user_may_access_branch
from core.permissions import HasRole, IsOrgMember


class AttendanceViewSet(TenantScopedAPIMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Attendance.objects.select_related("member", "branch")
    serializer_class = AttendanceSerializer

    def get_permissions(self):
        if self.action == "check_in":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "MEMBER":
            return qs.filter(member__user=user)
        if user.role == "TRAINER":
            return qs.filter(member__assigned_trainer=user)
        return qs.filter(branch_id__in=authorized_branch_ids(user) or [-1])

    @action(detail=False, methods=["post"], url_path="check-in")
    def check_in(self, request):
        serializer = CheckInSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not user_may_access_branch(request.user, data["branch"]):
            return Response(
                {"error": {"code": "PERMISSION_DENIED", "message": "You do not have access to this branch."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            attendance = check_in(
                member=data["member"],
                branch=data["branch"],
                method=data["method"],
                device_id=data.get("device_id", ""),
                recorded_by=request.user,
                override_reason=data.get("override_reason", ""),
            )
        except AttendanceEligibilityError as exc:
            return Response(
                {"error": {"code": exc.code, "message": str(exc)}},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)
