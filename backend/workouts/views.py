from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.api import STAFF_AND_TRAINER, TenantScopedAPIMixin
from core.permissions import HasRole, IsOrgMember
from workouts.models import Exercise, WorkoutLog, WorkoutProgram
from workouts.serializers import (
    ExerciseSerializer,
    ExerciseWriteSerializer,
    WorkoutDaySerializer,
    WorkoutDayWriteSerializer,
    WorkoutLogSerializer,
    WorkoutLogWriteSerializer,
    WorkoutProgramSerializer,
    WorkoutProgramWriteSerializer,
)


class ExerciseViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*STAFF_AND_TRAINER)]
        return [IsAuthenticated(), IsOrgMember()]

    def create(self, request, *args, **kwargs):
        serializer = ExerciseWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        exercise = serializer.save()
        return Response(ExerciseSerializer(exercise).data, status=status.HTTP_201_CREATED)


class WorkoutProgramViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = WorkoutProgram.objects.select_related("member", "trainer").prefetch_related("days__exercises__exercise")
    serializer_class = WorkoutProgramSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*STAFF_AND_TRAINER)]
        if self.action == "days" and self.request.method == "POST":
            return [IsAuthenticated(), IsOrgMember(), HasRole(*STAFF_AND_TRAINER)]
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "MEMBER":
            return qs.filter(member__user=user)
        if user.role == "TRAINER":
            return qs.filter(Q(trainer=user) | Q(member__assigned_trainer=user)).distinct()
        return qs.filter(member__home_branch=user.home_branch)

    def create(self, request, *args, **kwargs):
        serializer = WorkoutProgramWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        program = serializer.save()
        program = self.get_queryset().get(pk=program.pk)
        return Response(WorkoutProgramSerializer(program).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="days")
    def days(self, request, uuid=None):
        program = self.get_object()
        if request.method == "GET":
            days_qs = program.days.prefetch_related("exercises__exercise").order_by("day_index")
            return Response(WorkoutDaySerializer(days_qs, many=True).data)
        serializer = WorkoutDayWriteSerializer(
            data=request.data, context={"request": request, "program": program}
        )
        serializer.is_valid(raise_exception=True)
        day = serializer.save()
        day = program.days.prefetch_related("exercises__exercise").get(pk=day.pk)
        return Response(WorkoutDaySerializer(day).data, status=status.HTTP_201_CREATED)


class WorkoutLogViewSet(TenantScopedAPIMixin, viewsets.ModelViewSet):
    queryset = WorkoutLog.objects.select_related("member", "exercise", "workout_day_exercise")
    serializer_class = WorkoutLogSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        return [IsAuthenticated(), IsOrgMember()]

    def restrict_queryset(self, qs):
        user = self.request.user
        if user.role == "OWNER":
            return qs
        if user.role == "MEMBER":
            return qs.filter(member__user=user)
        if user.role == "TRAINER":
            return qs.filter(
                Q(member__assigned_trainer=user) | Q(member__workout_programs__trainer=user)
            ).distinct()
        return qs.filter(member__home_branch=user.home_branch)

    def create(self, request, *args, **kwargs):
        serializer = WorkoutLogWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        log = serializer.save()
        return Response(WorkoutLogSerializer(log).data, status=status.HTTP_201_CREATED)
