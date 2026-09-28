from rest_framework import serializers

from audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    actor = serializers.UUIDField(source="actor.uuid", read_only=True, allow_null=True)
    branch = serializers.UUIDField(source="branch.uuid", read_only=True, allow_null=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "resource_type",
            "resource_uuid",
            "actor",
            "branch",
            "before_state",
            "after_state",
            "occurred_at",
            "request_id",
            "system_initiated",
        ]
        read_only_fields = fields
