from django.db import transaction
from rest_framework import serializers

from branches.models import Branch

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Public-safe representation. Exposes `uuid` as `id` — the internal
    integer PK never appears in an API response (DEC-012)."""

    id = serializers.UUIDField(source="uuid", read_only=True)
    organization_id = serializers.UUIDField(source="organization.uuid", read_only=True)
    home_branch_id = serializers.UUIDField(source="home_branch.uuid", read_only=True, allow_null=True)
    trainer_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "phone",
            "role",
            "organization_id",
            "home_branch_id",
            "is_active",
            "date_joined",
            "trainer_profile",
        ]
        read_only_fields = fields

    def get_trainer_profile(self, obj):
        profile = getattr(obj, "trainer_profile", None)
        if profile is None:
            return None
        return {
            "id": str(profile.uuid),
            "specializations": profile.specializations or [],
            "certifications": profile.certifications or [],
            "compensation_model": profile.compensation_model,
            "compensation_rate": f"{profile.compensation_rate:.2f}",
            "bio": profile.bio or "",
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class StaffCreateSerializer(serializers.Serializer):
    """OWNER-only staff provisioning. STAFF_ADMIN and TRAINER only — never OWNER or MEMBER."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    role = serializers.ChoiceField(choices=[User.Role.STAFF_ADMIN, User.Role.TRAINER])
    home_branch_id = serializers.UUIDField()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_home_branch_id(self, value):
        request = self.context["request"]
        try:
            return Branch.objects.for_organization(request.user.organization).get(uuid=value)
        except Branch.DoesNotExist:
            raise serializers.ValidationError("Branch not found in your organization.")

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        branch = validated_data["home_branch_id"]
        user = User(
            organization=request.user.organization,
            home_branch=branch,
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            phone=validated_data.get("phone") or "",
            role=validated_data["role"],
            is_active=True,
        )
        user.set_password(validated_data["password"])
        user.full_clean()
        user.save()
        if user.role == User.Role.TRAINER:
            from trainers.models import TrainerProfile

            profile = TrainerProfile(user=user, organization=user.organization)
            profile.full_clean()
            profile.save()
        return user
