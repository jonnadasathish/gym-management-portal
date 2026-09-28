from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from trainers.models import TrainerProfile


class TrainerProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    user_id = serializers.UUIDField(source="user.uuid", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = TrainerProfile
        fields = [
            "id",
            "user_id",
            "email",
            "full_name",
            "phone",
            "specializations",
            "certifications",
            "compensation_model",
            "compensation_rate",
            "bio",
        ]
        read_only_fields = ["id", "user_id", "email", "full_name", "phone"]

    def validate_specializations(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Must be a list.")
        return value

    def validate_certifications(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Must be a list.")
        return value

    def update(self, instance, validated_data):
        request = self.context["request"]
        if request.user.role != "OWNER":
            if "compensation_model" in self.initial_data or "compensation_rate" in self.initial_data:
                raise PermissionDenied("Only OWNER may change compensation_model or compensation_rate.")
            validated_data.pop("compensation_model", None)
            validated_data.pop("compensation_rate", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance
