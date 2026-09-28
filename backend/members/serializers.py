from rest_framework import serializers

from accounts.models import User
from branches.models import Branch
from members.models import Member


class MemberSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    organization_id = serializers.UUIDField(source="organization.uuid", read_only=True)
    home_branch_id = serializers.UUIDField(write_only=True)
    home_branch = serializers.UUIDField(source="home_branch.uuid", read_only=True)
    assigned_trainer_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    assigned_trainer = serializers.SerializerMethodField()
    has_portal_login = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id",
            "organization_id",
            "member_code",
            "full_name",
            "phone",
            "email",
            "dob",
            "gender",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "home_branch_id",
            "home_branch",
            "assigned_trainer_id",
            "assigned_trainer",
            "joining_date",
            "status",
            "consent_status",
            "has_portal_login",
        ]
        read_only_fields = ["id", "organization_id", "status", "home_branch", "assigned_trainer", "has_portal_login"]
        extra_kwargs = {"member_code": {"required": False, "allow_blank": True}}

    def get_assigned_trainer(self, obj):
        return str(obj.assigned_trainer.uuid) if obj.assigned_trainer_id else None

    def get_has_portal_login(self, obj):
        return bool(obj.user_id)

    def validate_home_branch_id(self, value):
        request = self.context["request"]
        try:
            return Branch.objects.for_organization(request.user.organization).get(uuid=value)
        except Branch.DoesNotExist:
            raise serializers.ValidationError("Branch not found in your organization.")

    def validate_assigned_trainer_id(self, value):
        if value is None:
            return None
        request = self.context["request"]
        try:
            trainer = User.objects.for_organization(request.user.organization).get(uuid=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Trainer not found in your organization.")
        if trainer.role != User.Role.TRAINER:
            raise serializers.ValidationError("assigned_trainer must have role TRAINER.")
        return trainer

    def create(self, validated_data):
        request = self.context["request"]
        branch = validated_data.pop("home_branch_id")
        trainer = validated_data.pop("assigned_trainer_id", None)
        member_code = validated_data.get("member_code") or _next_member_code(request.user.organization)
        member = Member(
            organization=request.user.organization,
            home_branch=branch,
            assigned_trainer=trainer,
            member_code=member_code,
            **{k: v for k, v in validated_data.items() if k != "member_code"},
        )
        if not member.member_code:
            member.member_code = member_code
        member.full_clean()
        member.save()
        return member

    def update(self, instance, validated_data):
        if "home_branch_id" in validated_data:
            instance.home_branch = validated_data.pop("home_branch_id")
        if "assigned_trainer_id" in validated_data:
            instance.assigned_trainer = validated_data.pop("assigned_trainer_id")
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.organization = instance.organization  # never take a client org id
        instance.full_clean()
        instance.save()
        return instance


class ProvisionLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)


def _next_member_code(organization):
    last = (
        Member.objects.filter(organization=organization, member_code__startswith="GYM-")
        .order_by("-id")
        .first()
    )
    if last and last.member_code.startswith("GYM-"):
        try:
            n = int(last.member_code.split("-", 1)[1]) + 1
        except ValueError:
            n = Member.objects.filter(organization=organization).count() + 1
    else:
        n = Member.objects.filter(organization=organization).count() + 1
    return f"GYM-{n:06d}"
