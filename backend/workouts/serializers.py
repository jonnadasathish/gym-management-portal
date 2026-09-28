from django.db import transaction
from rest_framework import serializers

from accounts.models import User
from members.models import Member
from workouts.models import Exercise, WorkoutDay, WorkoutDayExercise, WorkoutLog, WorkoutProgram


class ExerciseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = Exercise
        fields = ["id", "name", "muscle_group", "equipment", "instructions", "media_url"]
        read_only_fields = fields


class ExerciseWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    muscle_group = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    equipment = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    instructions = serializers.CharField(required=False, allow_blank=True, default="")
    media_url = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")

    def create(self, validated_data):
        exercise = Exercise(
            organization=self.context["request"].user.organization,
            name=validated_data["name"],
            muscle_group=validated_data.get("muscle_group", ""),
            equipment=validated_data.get("equipment", ""),
            instructions=validated_data.get("instructions", ""),
            media_url=validated_data.get("media_url", ""),
        )
        exercise.full_clean()
        exercise.save()
        return exercise


class WorkoutDayExerciseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    exercise_id = serializers.UUIDField(source="exercise.uuid", read_only=True)
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)

    class Meta:
        model = WorkoutDayExercise
        fields = [
            "id",
            "exercise_id",
            "exercise_name",
            "target_sets",
            "target_reps",
            "target_weight",
            "rest_seconds",
            "notes",
            "order",
        ]
        read_only_fields = fields


class WorkoutDaySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    exercises = WorkoutDayExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutDay
        fields = ["id", "day_index", "label", "exercises"]
        read_only_fields = fields


class WorkoutProgramSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    member_id = serializers.UUIDField(source="member.uuid", read_only=True)
    trainer_id = serializers.UUIDField(source="trainer.uuid", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    trainer_name = serializers.CharField(source="trainer.full_name", read_only=True)
    days = WorkoutDaySerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutProgram
        fields = [
            "id",
            "member_id",
            "trainer_id",
            "member_name",
            "trainer_name",
            "name",
            "start_date",
            "end_date",
            "status",
            "days",
        ]
        read_only_fields = fields


class DayExerciseWriteSerializer(serializers.Serializer):
    exercise_id = serializers.UUIDField()
    target_sets = serializers.IntegerField(min_value=1)
    target_reps = serializers.IntegerField(min_value=1)
    target_weight = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    rest_seconds = serializers.IntegerField(min_value=0, required=False, default=0)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    order = serializers.IntegerField(min_value=0, required=False, default=0)

    def validate_exercise_id(self, value):
        org = self.context["request"].user.organization
        try:
            return Exercise.objects.for_organization(org).get(uuid=value)
        except Exercise.DoesNotExist:
            raise serializers.ValidationError("Exercise not found in your organization.")


class WorkoutDayWriteSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=255)
    day_index = serializers.IntegerField(min_value=0)
    exercises = DayExerciseWriteSerializer(many=True, required=False, default=list)

    def validate_day_index(self, value):
        program = self.context.get("program")
        if program is not None and WorkoutDay.objects.filter(program=program, day_index=value).exists():
            raise serializers.ValidationError("This day_index already exists on the program.")
        return value

    def create(self, validated_data):
        return create_day_with_exercises(self.context["program"], validated_data)


class WorkoutProgramWriteSerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    trainer_id = serializers.UUIDField(required=False)
    name = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=WorkoutProgram.Status.choices, required=False, default=WorkoutProgram.Status.ACTIVE
    )
    days = WorkoutDayWriteSerializer(many=True, required=False, default=list)

    def validate_member_id(self, value):
        org = self.context["request"].user.organization
        try:
            return Member.objects.for_organization(org).alive().get(uuid=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member not found in your organization.")

    def validate_trainer_id(self, value):
        org = self.context["request"].user.organization
        try:
            return User.objects.get(uuid=value, organization=org, role=User.Role.TRAINER, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Trainer not found in your organization.")

    def validate(self, attrs):
        user = self.context["request"].user
        member = attrs["member_id"]
        if user.role == "TRAINER":
            trainer = attrs.get("trainer_id")
            if trainer is not None and trainer.pk != user.pk:
                raise serializers.ValidationError({"trainer_id": "You can only assign yourself as trainer."})
            attrs["trainer_id"] = user
            if member.assigned_trainer_id != user.id:
                raise serializers.ValidationError(
                    {"member_id": "You can only create programs for your assigned members."}
                )
        elif attrs.get("trainer_id") is None:
            raise serializers.ValidationError({"trainer_id": "This field is required."})
        if user.role == "STAFF_ADMIN" and member.home_branch_id != user.home_branch_id:
            raise serializers.ValidationError({"member_id": "Member is not in your home branch."})

        seen_indexes = []
        for day in attrs.get("days", []):
            idx = day["day_index"]
            if idx in seen_indexes:
                raise serializers.ValidationError({"days": "day_index values must be unique within the program."})
            seen_indexes.append(idx)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        days_data = validated_data.pop("days", [])
        program = WorkoutProgram(
            organization=self.context["request"].user.organization,
            member=validated_data["member_id"],
            trainer=validated_data["trainer_id"],
            name=validated_data["name"],
            start_date=validated_data["start_date"],
            end_date=validated_data.get("end_date"),
            status=validated_data.get("status", WorkoutProgram.Status.ACTIVE),
        )
        program.full_clean()
        program.save()
        for day_data in days_data:
            create_day_with_exercises(program, day_data)
        return program


@transaction.atomic
def create_day_with_exercises(program, day_data):
    exercises_data = day_data.get("exercises") or []
    day = WorkoutDay(
        organization=program.organization,
        program=program,
        day_index=day_data["day_index"],
        label=day_data["label"],
    )
    day.full_clean()
    day.save()
    for item in exercises_data:
        prescription = WorkoutDayExercise(
            organization=program.organization,
            workout_day=day,
            exercise=item["exercise_id"],
            target_sets=item["target_sets"],
            target_reps=item["target_reps"],
            target_weight=item.get("target_weight"),
            rest_seconds=item.get("rest_seconds", 0),
            notes=item.get("notes", ""),
            order=item.get("order", 0),
        )
        prescription.full_clean()
        prescription.save()
    return day


class WorkoutLogSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    member_id = serializers.UUIDField(source="member.uuid", read_only=True)
    workout_day_exercise_id = serializers.SerializerMethodField()
    exercise_id = serializers.UUIDField(source="exercise.uuid", read_only=True)
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)

    class Meta:
        model = WorkoutLog
        fields = [
            "id",
            "member_id",
            "workout_day_exercise_id",
            "exercise_id",
            "exercise_name",
            "performed_on",
            "sets",
            "reps",
            "weight",
            "duration_seconds",
            "notes",
        ]
        read_only_fields = fields

    def get_workout_day_exercise_id(self, obj):
        if obj.workout_day_exercise_id:
            return obj.workout_day_exercise.uuid
        return None


class WorkoutLogWriteSerializer(serializers.Serializer):
    member_id = serializers.UUIDField(required=False)
    workout_day_exercise_id = serializers.UUIDField(required=False, allow_null=True)
    exercise_id = serializers.UUIDField(required=False)
    performed_on = serializers.DateField()
    sets = serializers.IntegerField(min_value=1)
    reps = serializers.IntegerField(min_value=1)
    weight = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    duration_seconds = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        request = self.context["request"]
        org = request.user.organization
        member_uuid = attrs.pop("member_id", None)

        if request.user.role == "MEMBER":
            try:
                member = Member.objects.for_organization(org).alive().get(user=request.user)
            except Member.DoesNotExist:
                raise serializers.ValidationError({"member_id": "No member profile is linked to this account."})
            if member_uuid and member.uuid != member_uuid:
                raise serializers.ValidationError({"member_id": "You can only log for yourself."})
        elif member_uuid:
            try:
                member = Member.objects.for_organization(org).alive().get(uuid=member_uuid)
            except Member.DoesNotExist:
                raise serializers.ValidationError({"member_id": "Member not found in your organization."})
        else:
            raise serializers.ValidationError({"member_id": "member_id is required."})

        if request.user.role == "STAFF_ADMIN" and member.home_branch_id != request.user.home_branch_id:
            raise serializers.ValidationError({"member_id": "Member is not in your home branch."})
        if request.user.role == "TRAINER":
            assigned = member.assigned_trainer_id == request.user.id
            coaches = member.workout_programs.filter(trainer=request.user).exists()
            if not assigned and not coaches:
                raise serializers.ValidationError({"member_id": "You can only log for your assigned members."})

        attrs["member"] = member

        prescription = None
        prescription_uuid = attrs.pop("workout_day_exercise_id", None)
        if prescription_uuid:
            try:
                prescription = (
                    WorkoutDayExercise.objects.for_organization(org)
                    .select_related("workout_day__program", "exercise")
                    .get(uuid=prescription_uuid)
                )
            except WorkoutDayExercise.DoesNotExist:
                raise serializers.ValidationError(
                    {"workout_day_exercise_id": "Prescription not found in your organization."}
                )
            if prescription.workout_day.program.member_id != member.id:
                raise serializers.ValidationError(
                    {"workout_day_exercise_id": "Log member must match the prescribed program member."}
                )
        attrs["workout_day_exercise"] = prescription

        exercise_uuid = attrs.pop("exercise_id", None)
        if exercise_uuid:
            try:
                exercise = Exercise.objects.for_organization(org).get(uuid=exercise_uuid)
            except Exercise.DoesNotExist:
                raise serializers.ValidationError({"exercise_id": "Exercise not found in your organization."})
        elif prescription is not None:
            exercise = prescription.exercise
        else:
            raise serializers.ValidationError({"exercise_id": "exercise_id is required for ad-hoc logs."})

        if prescription is not None and exercise.id != prescription.exercise_id:
            raise serializers.ValidationError({"exercise_id": "Exercise must match the prescribed exercise."})
        attrs["exercise"] = exercise
        return attrs

    def create(self, validated_data):
        log = WorkoutLog(
            organization=self.context["request"].user.organization,
            member=validated_data["member"],
            workout_day_exercise=validated_data.get("workout_day_exercise"),
            exercise=validated_data["exercise"],
            performed_on=validated_data["performed_on"],
            sets=validated_data["sets"],
            reps=validated_data["reps"],
            weight=validated_data.get("weight"),
            duration_seconds=validated_data.get("duration_seconds"),
            notes=validated_data.get("notes", ""),
        )
        log.full_clean()
        log.save()
        return log
