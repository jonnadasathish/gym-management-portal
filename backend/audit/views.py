from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from audit.models import AuditLog
from audit.serializers import AuditLogSerializer
from core.api import TenantScopedAPIMixin
from core.permissions import HasRole, IsOrgMember


class AuditLogViewSet(TenantScopedAPIMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """OWNER-only list. Append-only — no create/update/destroy routes."""

    queryset = AuditLog.objects.select_related("actor", "branch")
    serializer_class = AuditLogSerializer
    http_method_names = ["get", "head", "options"]

    def get_permissions(self):
        return [IsAuthenticated(), IsOrgMember(), HasRole("OWNER")]
