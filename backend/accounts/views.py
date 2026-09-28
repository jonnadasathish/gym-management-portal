"""Authentication endpoints implementing DEC-010 exactly:

- Access token: returned in the JSON response body only. The frontend
  holds it in memory (never localStorage) — that is a frontend concern,
  not something the backend can enforce, but the backend never sets it as
  a non-httpOnly cookie either, which would invite exactly the mistake
  DEC-010 is designed to avoid.
- Refresh token: NEVER returned in the JSON body. Set only as an
  `httpOnly`, `SameSite=Lax` cookie scoped to `/api/v1/auth/`, so
  JavaScript cannot read it and it is only ever sent back to the
  refresh/logout endpoints.
- Refresh rotates on every use (`ROTATE_REFRESH_TOKENS`); the old token is
  blacklisted (`BLACKLIST_AFTER_ROTATION`). Logout blacklists explicitly.
"""

from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import HasRole, IsOrgMember

from .models import User
from .serializers import LoginSerializer, StaffCreateSerializer, UserSerializer


def _set_refresh_cookie(response, refresh_token_str):
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        refresh_token_str,
        httponly=settings.JWT_REFRESH_COOKIE_HTTPONLY,
        secure=settings.JWT_REFRESH_COOKIE_SECURE,
        samesite=settings.JWT_REFRESH_COOKIE_SAMESITE,
        path=settings.JWT_REFRESH_COOKIE_PATH,
    )


def _clear_refresh_cookie(response):
    response.delete_cookie(settings.JWT_REFRESH_COOKIE_NAME, path=settings.JWT_REFRESH_COOKIE_PATH)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None or not user.is_active:
            return Response(
                {"error": {"code": "AUTHENTICATION_FAILED", "message": "Invalid email or password."}},
                status=401,
            )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {"data": {"access": str(access), "user": UserSerializer(user).data}}
        )
        _set_refresh_cookie(response, str(refresh))
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not raw_refresh:
            return Response(
                {"error": {"code": "AUTHENTICATION_REQUIRED", "message": "No refresh token present."}},
                status=401,
            )

        try:
            old_refresh = RefreshToken(raw_refresh)
            # Rotation: blacklist the old token, mint a fresh access+refresh
            # pair. This relies on ROTATE_REFRESH_TOKENS/BLACKLIST_AFTER_ROTATION
            # being handled by simplejwt's TokenRefreshSerializer semantics —
            # done explicitly here since we're not using the default view.
            new_access = old_refresh.access_token
            user_id_claim = old_refresh["user_uuid"]
            if getattr(settings, "SIMPLE_JWT", {}).get("BLACKLIST_AFTER_ROTATION"):
                old_refresh.blacklist()
            from django.contrib.auth import get_user_model

            user = get_user_model().objects.get(uuid=user_id_claim)
            new_refresh = RefreshToken.for_user(user)
        except TokenError:
            return Response(
                {"error": {"code": "AUTHENTICATION_REQUIRED", "message": "Refresh token is invalid or expired."}},
                status=401,
            )

        response = Response({"data": {"access": str(new_access)}})
        _set_refresh_cookie(response, str(new_refresh))
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if raw_refresh:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass

        response = Response(status=204)
        _clear_refresh_cookie(response)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"data": UserSerializer(request.user).data})


def _staff_queryset(user):
    """Tenant-scoped staff directory (non-MEMBER). Organization always from the caller."""
    return User.objects.for_organization(user.organization).exclude(role=User.Role.MEMBER)


def _get_staff_user(request, uuid):
    try:
        return _staff_queryset(request.user).get(uuid=uuid)
    except User.DoesNotExist:
        raise NotFound()


class StaffListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrgMember(), HasRole("OWNER")]
        return [IsAuthenticated(), IsOrgMember(), HasRole("OWNER", "STAFF_ADMIN")]

    def get(self, request):
        qs = _staff_queryset(request.user)
        if request.user.role != User.Role.OWNER:
            qs = qs.filter(is_active=True)
        if apps.is_installed("trainers"):
            qs = qs.select_related("trainer_profile")
        return Response({"data": UserSerializer(qs.order_by("full_name"), many=True).data})

    def post(self, request):
        serializer = StaffCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"data": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class StaffDeactivateView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember, HasRole("OWNER")]

    def post(self, request, uuid):
        target = _get_staff_user(request, uuid)
        if target.pk == request.user.pk:
            raise ValidationError("You cannot deactivate your own account.")
        if target.role == User.Role.OWNER:
            raise ValidationError("Cannot deactivate an OWNER account.")
        target.is_active = False
        target.save(update_fields=["is_active", "updated_at"])
        return Response({"data": UserSerializer(target).data})


class StaffActivateView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember, HasRole("OWNER")]

    def post(self, request, uuid):
        target = _get_staff_user(request, uuid)
        if target.role == User.Role.OWNER:
            raise ValidationError("Cannot activate an OWNER account.")
        target.is_active = True
        target.save(update_fields=["is_active", "updated_at"])
        return Response({"data": UserSerializer(target).data})
