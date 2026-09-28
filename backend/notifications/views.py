from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api import EnvelopeMixin, FRONT_DESK_ROLES, TenantScopedAPIMixin
from core.permissions import HasRole, IsOrgMember
from notifications.models import NotificationChannel, NotificationLog, NotificationTemplate
from notifications.serializers import EmitNotificationSerializer, NotificationLogSerializer, NotificationTemplateSerializer
from notifications.services import enqueue_notification


class NotificationLogViewSet(TenantScopedAPIMixin, viewsets.ReadOnlyModelViewSet):
    queryset = NotificationLog.objects.select_related("recipient_member", "recipient_user")
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role in ("OWNER", "STAFF_ADMIN"):
            return qs
        if user.role == "MEMBER":
            return qs.filter(Q(recipient_user=user) | Q(recipient_member__user=user))
        return qs.none()


class NotificationTemplateViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]


class NotificationEmitView(EnvelopeMixin, APIView):
    """Front-desk test helper: enqueue a notification without a vendor call."""

    permission_classes = [IsAuthenticated, IsOrgMember, HasRole(*FRONT_DESK_ROLES)]

    def post(self, request):
        serializer = EmitNotificationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        log = enqueue_notification(
            organization=request.user.organization,
            event_type=serializer.validated_data["event_type"],
            channel=serializer.validated_data.get("channel", NotificationChannel.IN_APP),
            member=serializer.validated_data["member_id"],
        )
        return Response(NotificationLogSerializer(log).data, status=status.HTTP_201_CREATED)
