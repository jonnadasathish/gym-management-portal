from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.api import FRONT_DESK_ROLES, TenantScopedAPIMixin
from core.permissions import HasRole, IsOrgMember
from data_migration.models import ImportJob
from data_migration.serializers import ImportJobSerializer, ImportJobWriteSerializer
from data_migration.services import MigrationStateError, confirm_import, preview_members_csv


class ImportJobViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = ImportJob.objects.prefetch_related("row_errors")
    serializer_class = ImportJobSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]

    def create(self, request, *args, **kwargs):
        serializer = ImportJobWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        job = serializer.save()
        return Response(ImportJobSerializer(job).data, status=status.HTTP_201_CREATED)

    def _reload(self, job):
        return ImportJob.objects.prefetch_related("row_errors").get(pk=job.pk)

    def _state_error(self, exc):
        return Response(
            {"error": {"code": exc.code, "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post"])
    def preview(self, request, uuid=None):
        job = self.get_object()
        try:
            job = preview_members_csv(job)
        except MigrationStateError as exc:
            return self._state_error(exc)
        return Response(ImportJobSerializer(self._reload(job)).data)

    @action(detail=True, methods=["post"])
    def confirm(self, request, uuid=None):
        job = self.get_object()
        try:
            job = confirm_import(job)
        except MigrationStateError as exc:
            return self._state_error(exc)
        return Response(ImportJobSerializer(self._reload(job)).data)
