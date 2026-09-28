from django.utils import timezone
from rest_framework import serializers

from members.models import Member
from progress.models import PersonalBest, ProgressEntry


def resolve_writable_member(request, member_uuid):
    """Resolve a member the caller may create progress records for.

    MEMBER: own profile only.
    TRAINER: members where assigned_trainer is this user (V1 assignment).
    OWNER / STAFF_ADMIN: any member in the authenticated user's organization.
    """
    user = request.user
    try:
        member = Member.objects.for_organization(user.organization).alive().get(uuid=member_uuid)
    except Member.DoesNotExist:
        raise serializers.ValidationError("Member not found in your organization.")

    if user.role == "MEMBER":
        if member.user_id != user.id:
            raise serializers.ValidationError("You can only record progress for your own profile.")
        return member
    if user.role == "TRAINER":
        if member.assigned_trainer_id != user.id:
            raise serializers.ValidationError("You can only record progress for your assigned members.")
        return member
    if user.role in ("OWNER", "STAFF_ADMIN"):
        return member
    raise serializers.ValidationError("You cannot record progress for this member.")


class ProgressEntrySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    member_id = serializers.UUIDField(source="member.uuid", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    bmi = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True, allow_null=True)

    class Meta:
        model = ProgressEntry
        fields = [
            "id",
            "member_id",
            "member_name",
            "recorded_at",
            "weight_kg",
            "height_cm",
            "bmi",
            "body_fat_pct",
            "measurements",
            "photo_url",
            "notes",
        ]
        read_only_fields = fields


class ProgressEntryWriteSerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    recorded_at = serializers.DateTimeField(required=False)
    weight_kg = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    height_cm = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    body_fat_pct = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    measurements = serializers.JSONField(required=False, default=dict)
    photo_url = serializers.CharField(max_length=512, required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_member_id(self, value):
        return resolve_writable_member(self.context["request"], value)

    def create(self, validated_data):
        entry = ProgressEntry(
            organization=self.context["request"].user.organization,
            member=validated_data["member_id"],
            recorded_at=validated_data.get("recorded_at") or timezone.now(),
            weight_kg=validated_data.get("weight_kg"),
            height_cm=validated_data.get("height_cm"),
            body_fat_pct=validated_data.get("body_fat_pct"),
            measurements=validated_data.get("measurements") or {},
            photo_url=validated_data.get("photo_url", ""),
            notes=validated_data.get("notes", ""),
        )
        entry.full_clean()
        entry.save()
        return entry


class PersonalBestSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    member_id = serializers.UUIDField(source="member.uuid", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)

    class Meta:
        model = PersonalBest
        fields = [
            "id",
            "member_id",
            "member_name",
            "exercise_name",
            "value",
            "unit",
            "achieved_at",
        ]
        read_only_fields = fields


class PersonalBestWriteSerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    exercise_name = serializers.CharField(max_length=255)
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
    unit = serializers.CharField(max_length=32)
    achieved_at = serializers.DateField()

    def validate_member_id(self, value):
        return resolve_writable_member(self.context["request"], value)

    def create(self, validated_data):
        record = PersonalBest(
            organization=self.context["request"].user.organization,
            member=validated_data["member_id"],
            exercise_name=validated_data["exercise_name"],
            value=validated_data["value"],
            unit=validated_data["unit"],
            achieved_at=validated_data["achieved_at"],
        )
        record.full_clean()
        record.save()
        return record
