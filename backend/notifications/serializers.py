from rest_framework import serializers

from members.models import Member
from notifications.models import NotificationChannel, NotificationEventType, NotificationLog, NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = NotificationTemplate
        fields = ["id", "event_type", "channel", "body", "is_active"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        template = NotificationTemplate(
            organization=self.context["request"].user.organization,
            **validated_data,
        )
        template.full_clean()
        template.save()
        return template


class NotificationLogSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    recipient_member_id = serializers.UUIDField(source="recipient_member.uuid", read_only=True, allow_null=True)
    recipient_user_id = serializers.UUIDField(source="recipient_user.uuid", read_only=True, allow_null=True)

    class Meta:
        model = NotificationLog
        fields = [
            "id",
            "recipient_member_id",
            "recipient_user_id",
            "event_type",
            "channel",
            "status",
            "provider_message_id",
            "error_detail",
            "sent_at",
            "payload",
        ]
        read_only_fields = fields


class EmitNotificationSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=NotificationEventType.choices)
    member_id = serializers.UUIDField()
    channel = serializers.ChoiceField(choices=NotificationChannel.choices, required=False, default=NotificationChannel.IN_APP)

    def validate_member_id(self, value):
        org = self.context["request"].user.organization
        try:
            return Member.objects.for_organization(org).alive().get(uuid=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member not found in your organization.")
