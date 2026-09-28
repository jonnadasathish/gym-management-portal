from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.api import STAFF_AND_TRAINER, TenantScopedAPIMixin, authorized_branch_ids
from core.permissions import HasRole, IsOrgMember
from progress.models import PersonalBest, ProgressEntry
from progress.serializers import (
    PersonalBestSerializer,
    PersonalBestWriteSerializer,
    ProgressEntrySerializer,
    ProgressEntryWriteSerializer,
)


def restrict_member_scoped_queryset(qs, user):
    """Same list scope as members: OWNER org; MEMBER own; TRAINER assigned; staff branch."""
    if user.role == "OWNER":
        return qs
    if user.role == "MEMBER":
        return qs.filter(member__user=user)
    if user.role == "TRAINER":
        return qs.filter(member__assigned_trainer=user)
    return qs.filter(member__home_branch_id__in=authorized_branch_ids(user) or [-1])


class ProgressEntryViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = ProgressEntry.objects.select_related("member")
    serializer_class = ProgressEntrySerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*STAFF_AND_TRAINER, "MEMBER")]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        return restrict_member_scoped_queryset(qs, self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = ProgressEntryWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        entry = serializer.save()
        return Response(ProgressEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


class PersonalBestViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = PersonalBest.objects.select_related("member")
    serializer_class = PersonalBestSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*STAFF_AND_TRAINER, "MEMBER")]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        return restrict_member_scoped_queryset(qs, self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = PersonalBestWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        record = serializer.save()
        return Response(PersonalBestSerializer(record).data, status=status.HTTP_201_CREATED)
