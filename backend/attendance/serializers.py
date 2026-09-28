import uuid

from rest_framework import serializers

from attendance.models import Attendance
from branches.models import Branch
from members.models import Member

QR_MEMBER_PREFIX = "gymportal:member:"


class AttendanceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    member = serializers.UUIDField(source="member.uuid", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    branch = serializers.UUIDField(source="branch.uuid", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "member",
            "member_name",
            "branch",
            "branch_name",
            "checkin_at",
            "checkout_at",
            "method",
            "device_id",
            "override_reason",
        ]
        read_only_fields = fields


class CheckInSerializer(serializers.Serializer):
    member_id = serializers.UUIDField(required=False)
    qr_payload = serializers.CharField(required=False, allow_blank=False)
    branch_id = serializers.UUIDField()
    method = serializers.ChoiceField(choices=Attendance.Method.choices, required=False)
    device_id = serializers.CharField(required=False, allow_blank=True, default="")
    override_reason = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_qr_payload(self, value):
        if not value.startswith(QR_MEMBER_PREFIX):
            raise serializers.ValidationError("Invalid QR payload.")
        raw_uuid = value[len(QR_MEMBER_PREFIX) :]
        try:
            return uuid.UUID(raw_uuid)
        except ValueError:
            raise serializers.ValidationError("Invalid QR payload.")

    def validate(self, attrs):
        request = self.context["request"]
        org = request.user.organization
        member_id = attrs.pop("member_id", None)
        qr_member_uuid = attrs.pop("qr_payload", None)

        if (member_id is None) == (qr_member_uuid is None):
            raise serializers.ValidationError("Exactly one of member_id or qr_payload is required.")

        if qr_member_uuid is not None:
            try:
                attrs["member"] = Member.objects.for_organization(org).get(uuid=qr_member_uuid)
            except Member.DoesNotExist:
                raise serializers.ValidationError({"qr_payload": "Member not found in your organization."})
            attrs.setdefault("method", Attendance.Method.QR)
        else:
            try:
                attrs["member"] = Member.objects.for_organization(org).get(uuid=member_id)
            except Member.DoesNotExist:
                raise serializers.ValidationError({"member_id": "Member not found in your organization."})
            attrs.setdefault("method", Attendance.Method.STAFF_SEARCH)

        try:
            attrs["branch"] = Branch.objects.for_organization(org).get(uuid=attrs.pop("branch_id"))
        except Branch.DoesNotExist:
            raise serializers.ValidationError({"branch_id": "Branch not found in your organization."})
        return attrs
