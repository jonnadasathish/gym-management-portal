from datetime import date

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.api import TenantScopedAPIMixin
from core.permissions import HasRole, IsOrgMember
from trainers.models import TrainerProfile
from trainers.serializers import TrainerProfileSerializer
from trainers.services import calculate_compensation


class TrainerProfileViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = TrainerProfile.objects.select_related("user")
    serializer_class = TrainerProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_permissions(self):
        if self.action == "compensation":
            return [IsAuthenticated(), IsOrgMember(), HasRole("OWNER")]
        if self.action in ("partial_update", "update"):
            return [IsAuthenticated(), IsOrgMember(), HasRole("OWNER", "TRAINER")]
        return [IsAuthenticated(), IsOrgMember(), HasRole("OWNER", "STAFF_ADMIN", "TRAINER")]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role in ("OWNER", "STAFF_ADMIN"):
            return qs
        if user.role == "TRAINER":
            return qs.filter(user=user)
        return qs.none()

    def get_object(self):
        qs = self.filter_queryset(self.get_queryset())
        lookup = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        obj = qs.filter(uuid=lookup).first() or qs.filter(user__uuid=lookup).first()
        if obj is None:
            raise NotFound()
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=["get"])
    def compensation(self, request, uuid=None):
        profile = self.get_object()
        start_raw = request.query_params.get("start")
        end_raw = request.query_params.get("end")
        if not start_raw or not end_raw:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "start and end query parameters are required (YYYY-MM-DD).",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            start_date = date.fromisoformat(start_raw)
            end_date = date.fromisoformat(end_raw)
        except ValueError:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "start and end must be ISO dates (YYYY-MM-DD).",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if start_date > end_date:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "start must be on or before end.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = calculate_compensation(
            trainer_user=profile.user,
            start_date=start_date,
            end_date=end_date,
        )
        if payload.get("compensation_rate") is not None:
            payload["compensation_rate"] = f"{payload['compensation_rate']:.2f}"
        if payload.get("computed_amount") is not None:
            payload["computed_amount"] = f"{payload['computed_amount']:.2f}"
        payload["trainer_id"] = str(payload["trainer_id"])
        payload["start_date"] = start_date.isoformat()
        payload["end_date"] = end_date.isoformat()
        return Response(payload)
