from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.serializers import UserSerializer
from classes.models import Booking, ClassOccurrence, GymClass
from classes.serializers import (
    BookActionSerializer,
    BookingSerializer,
    ClassOccurrenceSerializer,
    GymClassSerializer,
    GymClassWriteSerializer,
    OccurrenceWriteSerializer,
)
from classes.services import BookingError, book_occurrence, cancel_booking, cancel_occurrence, create_occurrence
from core.api import EnvelopeMixin, FRONT_DESK_ROLES, TenantScopedAPIMixin, authorized_branch_ids
from core.permissions import HasRole, IsOrgMember


class TrainerListView(EnvelopeMixin, viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsOrgMember]

    def list(self, request):
        qs = User.objects.filter(organization=request.user.organization, role=User.Role.TRAINER, is_active=True)
        if request.user.role == "TRAINER":
            qs = qs.filter(pk=request.user.pk)
        return Response(UserSerializer(qs.order_by("full_name"), many=True).data)


class GymClassViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = GymClass.objects.select_related("branch", "trainer")
    serializer_class = GymClassSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "TRAINER":
            return qs.filter(trainer=user)
        if user.role == "MEMBER":
            return qs.filter(status=GymClass.Status.ACTIVE)
        return qs.filter(branch_id__in=authorized_branch_ids(user) or [-1])

    def create(self, request, *args, **kwargs):
        serializer = GymClassWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        gym_class = serializer.save()
        return Response(GymClassSerializer(gym_class).data, status=status.HTTP_201_CREATED)


class ClassOccurrenceViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = ClassOccurrence.objects.select_related("gym_class").annotate(
        annotated_booked_count=Count("bookings", filter=Q(bookings__status=Booking.Status.BOOKED))
    )
    serializer_class = ClassOccurrenceSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action in ("create", "cancel"):
            return [IsAuthenticated(), IsOrgMember(), HasRole(*FRONT_DESK_ROLES)]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "TRAINER":
            return qs.filter(gym_class__trainer=user)
        if user.role == "MEMBER":
            return qs.filter(status=ClassOccurrence.Status.SCHEDULED)
        return qs.filter(gym_class__branch_id__in=authorized_branch_ids(user) or [-1])

    def create(self, request, *args, **kwargs):
        serializer = OccurrenceWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            occurrence = create_occurrence(
                gym_class=serializer.validated_data["gym_class_id"],
                start_time=serializer.validated_data["start_time"],
                end_time=serializer.validated_data["end_time"],
                capacity_override=serializer.validated_data.get("capacity_override"),
            )
        except BookingError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(ClassOccurrenceSerializer(occurrence).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, uuid=None):
        occurrence = self.get_object()
        try:
            occurrence = cancel_occurrence(occurrence_id=occurrence.id)
        except BookingError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(ClassOccurrenceSerializer(occurrence).data)


class BookingViewSet(TenantScopedAPIMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Booking.objects.select_related("occurrence", "occurrence__gym_class", "member")
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action in ("book", "cancel"):
            return [IsAuthenticated(), IsOrgMember()]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "MEMBER":
            return qs.filter(member__user=user)
        if user.role == "TRAINER":
            return qs.filter(occurrence__gym_class__trainer=user)
        return qs.filter(occurrence__gym_class__branch_id__in=authorized_branch_ids(user) or [-1])

    @action(detail=False, methods=["post"])
    def book(self, request):
        if request.user.role == "TRAINER":
            return Response(
                {"error": {"code": "PERMISSION_DENIED", "message": "Trainers cannot create bookings."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = BookActionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            booking = book_occurrence(
                occurrence_id=serializer.validated_data["occurrence"].id,
                member=serializer.validated_data["member"],
                waitlist_if_full=serializer.validated_data.get("waitlist_if_full", False),
            )
        except BookingError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, uuid=None):
        booking = self.get_object()
        if request.user.role == "MEMBER" and booking.member.user_id != request.user.id:
            return Response(
                {"error": {"code": "PERMISSION_DENIED", "message": "You can only cancel your own booking."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.role == "TRAINER":
            return Response(
                {"error": {"code": "PERMISSION_DENIED", "message": "Trainers cannot cancel bookings."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            booking = cancel_booking(booking_id=booking.id)
        except BookingError as exc:
            return Response({"error": {"code": exc.code, "message": str(exc)}}, status=status.HTTP_409_CONFLICT)
        return Response(BookingSerializer(booking).data)
