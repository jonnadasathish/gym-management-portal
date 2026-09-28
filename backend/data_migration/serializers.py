from rest_framework import serializers

from data_migration.models import ImportJob, ImportRowError


class ImportRowErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportRowError
        fields = ["row_number", "raw_data", "error_messages"]
        read_only_fields = fields


class ImportJobSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    row_errors = ImportRowErrorSerializer(many=True, read_only=True)

    class Meta:
        model = ImportJob
        fields = [
            "id",
            "entity_type",
            "status",
            "raw_csv",
            "total_rows",
            "valid_rows",
            "error_rows",
            "report",
            "row_errors",
        ]
        read_only_fields = fields


class ImportJobWriteSerializer(serializers.Serializer):
    raw_csv = serializers.CharField()
    entity_type = serializers.ChoiceField(choices=ImportJob.EntityType.choices)

    def create(self, validated_data):
        request = self.context["request"]
        job = ImportJob(
            organization=request.user.organization,
            uploaded_by=request.user,
            raw_csv=validated_data["raw_csv"],
            entity_type=validated_data["entity_type"],
            status=ImportJob.Status.UPLOADED,
        )
        job.full_clean()
        job.save()
        return job
