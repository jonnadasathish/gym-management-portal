from datetime import timedelta

from rest_framework import serializers

from members.models import Member
from memberships.models import FreezeRequest, Membership, MembershipFreeze, MembershipPlan


class MembershipPlanSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    organization_id = serializers.UUIDField(source="organization.uuid", read_only=True)

    class Meta:
        model = MembershipPlan
        fields = [
            "id",
            "organization_id",
            "name",
            "duration_days",
            "price",
            "billing_frequency",
            "freeze_allowed",
            "max_freeze_days",
            "status",
        ]
        read_only_fields = ["id", "organization_id"]

    def create(self, validated_data):
        validated_data["organization"] = self.context["request"].user.organization
        return super().create(validated_data)


class MembershipFreezeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipFreeze
        fields = ["id", "start_date", "end_date", "reason", "notes", "revised_end_date", "created_at"]
        read_only_fields = fields


class FreezeRequestSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    membership = serializers.UUIDField(source="membership.uuid", read_only=True)
    member = serializers.UUIDField(source="member.uuid", read_only=True)

    class Meta:
        model = FreezeRequest
        fields = [
            "id",
            "membership",
            "member",
            "start_date",
            "end_date",
            "reason",
            "notes",
            "status",
            "created_at",
        ]
        read_only_fields = fields


class MembershipSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    member_id = serializers.UUIDField(write_only=True)
    plan_id = serializers.UUIDField(write_only=True)
    member = serializers.UUIDField(source="member.uuid", read_only=True)
    plan = serializers.UUIDField(source="plan.uuid", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    freezes = MembershipFreezeSerializer(many=True, read_only=True)
    freeze_requests = FreezeRequestSerializer(many=True, read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "member_id",
            "plan_id",
            "member",
            "plan",
            "plan_name",
            "member_name",
            "start_date",
            "end_date",
            "status",
            "price",
            "discount",
            "freezes",
            "freeze_requests",
        ]
        read_only_fields = [
            "id",
            "member",
            "plan",
            "plan_name",
            "member_name",
            "status",
            "freezes",
            "freeze_requests",
        ]
        extra_kwargs = {
            "end_date": {"required": False},
            "price": {"required": False},
            "discount": {"required": False},
        }

    def validate_member_id(self, value):
        org = self.context["request"].user.organization
        try:
            return Member.objects.for_organization(org).alive().get(uuid=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member not found in your organization.")

    def validate_plan_id(self, value):
        org = self.context["request"].user.organization
        try:
            return MembershipPlan.objects.for_organization(org).get(uuid=value)
        except MembershipPlan.DoesNotExist:
            raise serializers.ValidationError("Plan not found in your organization.")

    def create(self, validated_data):
        request = self.context["request"]
        member = validated_data.pop("member_id")
        plan = validated_data.pop("plan_id")
        start_date = validated_data["start_date"]
        end_date = validated_data.get("end_date") or (start_date + timedelta(days=plan.duration_days))
        price = validated_data.get("price", plan.price)
        discount = validated_data.get("discount", 0)
        membership = Membership(
            organization=request.user.organization,
            member=member,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            price=price,
            discount=discount,
            created_by=request.user,
        )
        membership.full_clean()
        membership.save()
        from memberships.services import _enqueue_membership_created_notification, sync_member_status

        _enqueue_membership_created_notification(membership)
        sync_member_status(membership.member)
        return membership


class FreezeActionSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(max_length=255)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class RenewActionSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField(required=False)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
