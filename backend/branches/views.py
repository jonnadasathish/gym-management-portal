from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from branches.models import Branch
from branches.serializers import BranchSerializer
from core.api import TenantScopedAPIMixin, authorized_branch_ids
from core.permissions import IsOrgMember


class BranchViewSet(TenantScopedAPIMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        return qs.filter(id__in=authorized_branch_ids(user) or [-1])
