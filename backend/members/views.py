from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.api import FRONT_DESK_ROLES, TenantScopedAPIMixin, authorized_branch_ids
from core.permissions import HasRole, IsOrgMember
from members.models import Member
from members.serializers import MemberSerializer, ProvisionLoginSerializer
from members.services import MemberPortalError, provision_member_login


class MemberViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "phone", "member_code", "email"]
    ordering_fields = ["full_name", "joining_date", "member_code"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "provision_login"):
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        qs = qs.alive()
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "MEMBER":
            return qs.filter(user=user)
        if user.role == "TRAINER":
            return qs.filter(assigned_trainer=user)
        return qs.filter(home_branch_id__in=authorized_branch_ids(user) or [-1])

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["get"])
    def qr(self, request, uuid=None):
        member = self.get_object()
        return Response({"qr_payload": f"gymportal:member:{member.uuid}", "member_id": str(member.uuid)})

    @action(detail=False, methods=["get"])
    def me(self, request):
        if request.user.role != "MEMBER":
            return Response(
                {"error": {"code": "PERMISSION_DENIED", "message": "Only members can load /members/me/."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            member = self.get_queryset().get(user=request.user)
        except Member.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "No member profile is linked to this account."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(MemberSerializer(member).data)

    @action(detail=True, methods=["post"], url_path="provision-login")
    def provision_login(self, request, uuid=None):
        member = self.get_object()
        serializer = ProvisionLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            member = provision_member_login(
                member=member,
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except MemberPortalError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(MemberSerializer(member).data)
