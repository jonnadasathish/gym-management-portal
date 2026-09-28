from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.api import FRONT_DESK_ROLES, TenantScopedAPIMixin, authorized_branch_ids
from core.exceptions import ConflictError
from core.permissions import HasRole, IsOrgMember
from memberships.models import FreezeRequest, Membership, MembershipPlan
from memberships.serializers import (
    FreezeActionSerializer,
    FreezeRequestSerializer,
    MembershipPlanSerializer,
    MembershipSerializer,
    RenewActionSerializer,
)
from memberships.services import (
    MembershipStateError,
    apply_freeze,
    approve_freeze_request,
    create_freeze_request,
    reject_freeze_request,
    renew_membership,
    unfreeze_membership,
)


class MembershipPlanViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        return [IsAuthenticated(), IsOrgMember()]


class MembershipViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = Membership.objects.select_related("member", "plan").prefetch_related(
        "freezes",
        Prefetch(
            "freeze_requests",
            queryset=FreezeRequest.objects.select_related("membership", "member"),
        ),
    )
    serializer_class = MembershipSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "request_freeze":
            return [IsAuthenticated(), IsOrgMember(), HasRole("MEMBER")]
        if self.action in ("create", "freeze", "unfreeze", "renew"):
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            scoped = qs
        elif user.role == "MEMBER":
            scoped = qs.filter(member__user=user)
        elif user.role == "TRAINER":
            scoped = qs.filter(member__assigned_trainer=user)
        else:
            scoped = qs.filter(member__home_branch_id__in=authorized_branch_ids(user) or [-1])
        member_uuid = self.request.query_params.get("member")
        if member_uuid:
            scoped = scoped.filter(member__uuid=member_uuid)
        return scoped

    def _state_error(self, exc):
        raise ConflictError(detail=str(exc))

    @action(detail=True, methods=["post"])
    def freeze(self, request, uuid=None):
        membership = self.get_object()
        serializer = FreezeActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            membership, freeze = apply_freeze(
                membership_id=membership.id,
                requested_by=request.user,
                **serializer.validated_data,
            )
        except MembershipStateError as exc:
            self._state_error(exc)
        except DjangoValidationError as exc:
            raise ConflictError(detail=str(exc))
        return Response(MembershipSerializer(membership, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def unfreeze(self, request, uuid=None):
        membership = self.get_object()
        try:
            membership = unfreeze_membership(membership_id=membership.id)
        except MembershipStateError as exc:
            self._state_error(exc)
        return Response(MembershipSerializer(membership, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def renew(self, request, uuid=None):
        membership = self.get_object()
        serializer = RenewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        plan = membership.plan
        if data.get("plan_id"):
            try:
                plan = MembershipPlan.objects.for_organization(request.user.organization).get(uuid=data["plan_id"])
            except MembershipPlan.DoesNotExist:
                return Response(
                    {"error": {"code": "VALIDATION_ERROR", "message": "Plan not found in your organization."}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        start_date = data["start_date"]
        end_date = data.get("end_date") or (start_date + timedelta(days=plan.duration_days))
        try:
            new_membership = renew_membership(
                membership_id=membership.id,
                new_plan=plan,
                new_start_date=start_date,
                new_end_date=end_date,
                price=data.get("price", plan.price),
                discount=data.get("discount", 0),
                created_by=request.user,
            )
        except MembershipStateError as exc:
            self._state_error(exc)
        return Response(
            MembershipSerializer(new_membership, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="request-freeze")
    def request_freeze(self, request, uuid=None):
        membership = self.get_object()
        serializer = FreezeActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        freeze_request = create_freeze_request(
            membership=membership,
            requested_by=request.user,
            **serializer.validated_data,
        )
        return Response(
            FreezeRequestSerializer(freeze_request).data,
            status=status.HTTP_201_CREATED,
        )


class FreezeRequestViewSet(TenantScopedAPIMixin, viewsets.ReadOnlyModelViewSet):
    queryset = FreezeRequest.objects.select_related("membership", "member")
    serializer_class = FreezeRequestSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action in ("approve", "reject"):
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            scoped = qs
        elif user.role == "MEMBER":
            scoped = qs.filter(member__user=user)
        elif user.role == "TRAINER":
            scoped = qs.filter(member__assigned_trainer=user)
        else:
            scoped = qs.filter(member__home_branch_id__in=authorized_branch_ids(user) or [-1])
        member_uuid = self.request.query_params.get("member")
        if member_uuid:
            scoped = scoped.filter(member__uuid=member_uuid)
        return scoped

    def _state_error(self, exc):
        raise ConflictError(detail=str(exc))

    @action(detail=True, methods=["post"])
    def approve(self, request, uuid=None):
        freeze_request = self.get_object()
        try:
            freeze_request = approve_freeze_request(
                freeze_request_id=freeze_request.id,
                reviewed_by=request.user,
            )
        except MembershipStateError as exc:
            self._state_error(exc)
        except DjangoValidationError as exc:
            raise ConflictError(detail=str(exc))
        freeze_request.refresh_from_db()
        return Response(FreezeRequestSerializer(freeze_request).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, uuid=None):
        freeze_request = self.get_object()
        try:
            freeze_request = reject_freeze_request(
                freeze_request_id=freeze_request.id,
                reviewed_by=request.user,
            )
        except MembershipStateError as exc:
            self._state_error(exc)
        return Response(FreezeRequestSerializer(freeze_request).data)
