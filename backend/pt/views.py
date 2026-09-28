from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.api import FRONT_DESK_ROLES, TenantScopedAPIMixin
from core.permissions import HasRole, IsOrgMember
from pt.models import PTPackage, PTSession
from pt.serializers import (
    PTPackageSerializer,
    PTPackageWriteSerializer,
    PTSessionSerializer,
    RescheduleSessionSerializer,
    ScheduleSessionSerializer,
)
from pt.services import (
    PTStateError,
    cancel_session,
    complete_session,
    mark_no_show,
    reschedule_session,
    schedule_session,
)


class PTPackageViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = PTPackage.objects.select_related("member", "trainer")
    serializer_class = PTPackageSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "MEMBER":
            return qs.filter(member__user=user)
        if user.role == "TRAINER":
            return qs.filter(trainer=user)
        return qs.filter(member__home_branch=user.home_branch)

    def create(self, request, *args, **kwargs):
        serializer = PTPackageWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        package = serializer.save()
        return Response(PTPackageSerializer(package).data, status=status.HTTP_201_CREATED)


class PTSessionViewSet(TenantScopedAPIMixin, viewsets.ReadOnlyModelViewSet):
    queryset = PTSession.objects.select_related("package", "member", "trainer")
    serializer_class = PTSessionSerializer

    def get_permissions(self):
        if self.action == "schedule":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES, "TRAINER")]
        if self.action in ("complete", "cancel", "no_show", "reschedule"):
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES, "TRAINER")]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "MEMBER":
            return qs.filter(member__user=user)
        if user.role == "TRAINER":
            return qs.filter(trainer=user)
        return qs.filter(member__home_branch=user.home_branch)

    @action(detail=False, methods=["post"])
    def schedule(self, request):
        serializer = ScheduleSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            package = PTPackage.objects.for_organization(request.user.organization).get(
                uuid=serializer.validated_data["package_id"]
            )
        except PTPackage.DoesNotExist:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Package not found in your organization."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.role == "TRAINER" and package.trainer_id != request.user.id:
            return Response(
                {"error": {"code": "PERMISSION_DENIED", "message": "You can only schedule your own PT clients."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            session = schedule_session(
                package_id=package.id,
                scheduled_at=serializer.validated_data["scheduled_at"],
                duration_minutes=serializer.validated_data.get("duration_minutes", 60),
                notes=serializer.validated_data.get("notes", ""),
            )
        except PTStateError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(PTSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def reschedule(self, request, uuid=None):
        session = self.get_object()
        serializer = RescheduleSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            session = reschedule_session(
                session_id=session.id,
                scheduled_at=serializer.validated_data["scheduled_at"],
                duration_minutes=serializer.validated_data.get("duration_minutes"),
            )
        except PTStateError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(PTSessionSerializer(session).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, uuid=None):
        session = self.get_object()
        try:
            session, _package = complete_session(session_id=session.id)
        except PTStateError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(PTSessionSerializer(session).data)

    @action(detail=True, methods=["post"], url_path="no-show")
    def no_show(self, request, uuid=None):
        session = self.get_object()
        try:
            session = mark_no_show(session_id=session.id)
        except PTStateError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(PTSessionSerializer(session).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, uuid=None):
        session = self.get_object()
        try:
            session = cancel_session(session_id=session.id)
        except PTStateError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(PTSessionSerializer(session).data)
