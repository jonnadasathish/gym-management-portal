from rest_framework import serializers

from branches.models import Branch


class BranchSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = Branch
        fields = ["id", "name", "address", "phone", "status"]
        read_only_fields = fields
