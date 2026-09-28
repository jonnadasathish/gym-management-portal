from rest_framework import serializers

from accounts.models import User
from branches.models import Branch
from classes.models import Booking, ClassOccurrence, GymClass
from core.api import user_may_access_branch
from members.models import Member


class GymClassSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    branch_id = serializers.UUIDField(source="branch.uuid", read_only=True)
    trainer_id = serializers.UUIDField(source="trainer.uuid", read_only=True, allow_null=True)

    class Meta:
        model = GymClass
        fields = ["id", "name", "branch_id", "trainer_id", "room", "capacity", "status"]
        read_only_fields = fields


class ClassOccurrenceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    gym_class_id = serializers.UUIDField(source="gym_class.uuid", read_only=True)
    gym_class_name = serializers.CharField(source="gym_class.name", read_only=True)
    capacity = serializers.IntegerField(source="effective_capacity", read_only=True)
    booked_count = serializers.SerializerMethodField()

    class Meta:
        model = ClassOccurrence
        fields = [
            "id",
            "gym_class_id",
            "gym_class_name",
            "start_time",
            "end_time",
            "status",
            "capacity",
            "booked_count",
        ]
        read_only_fields = fields

    def get_booked_count(self, obj):
        annotated = getattr(obj, "annotated_booked_count", None)
        if annotated is not None:
            return annotated
        return obj.bookings.filter(status=Booking.Status.BOOKED).count()


class BookingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    occurrence_id = serializers.UUIDField(source="occurrence.uuid", read_only=True)
    member_id = serializers.UUIDField(source="member.uuid", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    gym_class_name = serializers.CharField(source="occurrence.gym_class.name", read_only=True)
    start_time = serializers.DateTimeField(source="occurrence.start_time", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "occurrence_id",
            "member_id",
            "member_name",
            "gym_class_name",
            "start_time",
            "status",
            "booked_at",
            "cancelled_at",
        ]
        read_only_fields = fields


class GymClassWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    branch_id = serializers.UUIDField()
    trainer_id = serializers.UUIDField(required=False, allow_null=True)
    room = serializers.CharField(required=False, allow_blank=True, default="")
    capacity = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=GymClass.Status.choices, required=False, default=GymClass.Status.ACTIVE)

    def validate_branch_id(self, value):
        user = self.context["request"].user
        try:
            branch = Branch.objects.for_organization(user.organization).get(uuid=value)
        except Branch.DoesNotExist:
            raise serializers.ValidationError("Branch not found in your organization.")
        if not user_may_access_branch(user, branch):
            raise serializers.ValidationError("You do not have access to this branch.")
        return branch

    def validate_trainer_id(self, value):
        if value is None:
            return None
        user = self.context["request"].user
        try:
            return User.objects.get(
                uuid=value, organization=user.organization, role=User.Role.TRAINER, is_active=True
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("Trainer not found in your organization.")

    def create(self, validated_data):
        gym_class = GymClass(
            organization=self.context["request"].user.organization,
            branch=validated_data["branch_id"],
            trainer=validated_data.get("trainer_id"),
            name=validated_data["name"],
            room=validated_data.get("room", ""),
            capacity=validated_data["capacity"],
            status=validated_data.get("status", GymClass.Status.ACTIVE),
        )
        gym_class.full_clean()
        gym_class.save()
        return gym_class


class OccurrenceWriteSerializer(serializers.Serializer):
    gym_class_id = serializers.UUIDField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    capacity_override = serializers.IntegerField(required=False, allow_null=True, min_value=1)

    def validate_gym_class_id(self, value):
        user = self.context["request"].user
        try:
            gym_class = GymClass.objects.for_organization(user.organization).select_related("branch", "trainer").get(
                uuid=value
            )
        except GymClass.DoesNotExist:
            raise serializers.ValidationError("Class not found in your organization.")
        if not user_may_access_branch(user, gym_class.branch):
            raise serializers.ValidationError("You do not have access to this class branch.")
        return gym_class


class BookActionSerializer(serializers.Serializer):
    occurrence_id = serializers.UUIDField()
    member_id = serializers.UUIDField(required=False)
    waitlist_if_full = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        request = self.context["request"]
        org = request.user.organization
        try:
            attrs["occurrence"] = ClassOccurrence.objects.for_organization(org).select_related("gym_class").get(
                uuid=attrs.pop("occurrence_id")
            )
        except ClassOccurrence.DoesNotExist:
            raise serializers.ValidationError({"occurrence_id": "Occurrence not found in your organization."})

        member_uuid = attrs.pop("member_id", None)
        if request.user.role == "MEMBER":
            try:
                attrs["member"] = Member.objects.for_organization(org).alive().get(user=request.user)
            except Member.DoesNotExist:
                raise serializers.ValidationError({"member_id": "No member profile is linked to this account."})
        elif member_uuid:
            try:
                attrs["member"] = Member.objects.for_organization(org).alive().get(uuid=member_uuid)
            except Member.DoesNotExist:
                raise serializers.ValidationError({"member_id": "Member not found in your organization."})
        else:
            raise serializers.ValidationError({"member_id": "member_id is required for staff bookings."})
        return attrs
