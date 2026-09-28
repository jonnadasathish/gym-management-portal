from rest_framework import serializers

from pt.models import PTPackage, PTSession


class PTPackageSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    member_id = serializers.UUIDField(source="member.uuid", read_only=True)
    trainer_id = serializers.UUIDField(source="trainer.uuid", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    trainer_name = serializers.CharField(source="trainer.full_name", read_only=True)
    sessions_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = PTPackage
        fields = [
            "id",
            "member_id",
            "trainer_id",
            "member_name",
            "trainer_name",
            "plan_name",
            "sessions_purchased",
            "sessions_consumed",
            "sessions_remaining",
            "price",
            "expiry_date",
        ]
        read_only_fields = fields


class PTSessionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    package_id = serializers.UUIDField(source="package.uuid", read_only=True)
    member_id = serializers.UUIDField(source="member.uuid", read_only=True)
    trainer_id = serializers.UUIDField(source="trainer.uuid", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    trainer_name = serializers.CharField(source="trainer.full_name", read_only=True)

    class Meta:
        model = PTSession
        fields = [
            "id",
            "package_id",
            "member_id",
            "trainer_id",
            "member_name",
            "trainer_name",
            "scheduled_at",
            "duration_minutes",
            "status",
            "notes",
        ]
        read_only_fields = fields


class ScheduleSessionSerializer(serializers.Serializer):
    package_id = serializers.UUIDField()
    scheduled_at = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(required=False, default=60)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class RescheduleSessionSerializer(serializers.Serializer):
    scheduled_at = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(required=False, min_value=1)


class PTPackageWriteSerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    trainer_id = serializers.UUIDField()
    plan_name = serializers.CharField(max_length=255)
    sessions_purchased = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = serializers.DateField(required=False, allow_null=True)

    def validate_member_id(self, value):
        from members.models import Member

        org = self.context["request"].user.organization
        try:
            return Member.objects.for_organization(org).alive().get(uuid=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member not found in your organization.")

    def validate_trainer_id(self, value):
        from accounts.models import User

        org = self.context["request"].user.organization
        try:
            return User.objects.get(uuid=value, organization=org, role=User.Role.TRAINER, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Trainer not found in your organization.")

    def create(self, validated_data):
        package = PTPackage(
            organization=self.context["request"].user.organization,
            member=validated_data["member_id"],
            trainer=validated_data["trainer_id"],
            plan_name=validated_data["plan_name"],
            sessions_purchased=validated_data["sessions_purchased"],
            price=validated_data["price"],
            expiry_date=validated_data.get("expiry_date"),
        )
        package.full_clean()
        package.save()
        return package
