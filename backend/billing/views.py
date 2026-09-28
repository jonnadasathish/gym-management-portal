from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from billing.models import Invoice
from billing.serializers import InvoiceSerializer
from core.api import FRONT_DESK_ROLES, TenantScopedAPIMixin, authorized_branch_ids
from core.permissions import HasRole, IsOrgMember


class InvoiceViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("member").prefetch_related("line_items")
    serializer_class = InvoiceSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
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
