from rest_framework import serializers

from accounts.models import User
from branches.models import Branch
from core.api import user_may_access_branch
from crm.models import Lead, LeadActivity
from memberships.models import MembershipPlan


class LeadSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    branch_id = serializers.UUIDField(write_only=True)
    branch = serializers.UUIDField(source="branch.uuid", read_only=True)
    interested_plan_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    interested_plan = serializers.SerializerMethodField()
    assigned_staff_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    assigned_staff = serializers.SerializerMethodField()
    converted_member_id = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            "id",
            "branch_id",
            "branch",
            "name",
            "phone",
            "source",
            "interested_plan_id",
            "interested_plan",
            "assigned_staff_id",
            "assigned_staff",
            "trial_date",
            "status",
            "next_follow_up",
            "notes",
            "converted_member_id",
        ]
        read_only_fields = ["id", "branch", "interested_plan", "assigned_staff", "converted_member_id"]

    def get_interested_plan(self, obj):
        return str(obj.interested_plan.uuid) if obj.interested_plan_id else None

    def get_assigned_staff(self, obj):
        return str(obj.assigned_staff.uuid) if obj.assigned_staff_id else None

    def get_converted_member_id(self, obj):
        return str(obj.converted_member.uuid) if obj.converted_member_id else None

    def validate_branch_id(self, value):
        request = self.context["request"]
        try:
            branch = Branch.objects.for_organization(request.user.organization).get(uuid=value)
        except Branch.DoesNotExist:
            raise serializers.ValidationError("Branch not found in your organization.")
        if not user_may_access_branch(request.user, branch):
            raise serializers.ValidationError("You do not have access to this branch.")
        return branch

    def validate_interested_plan_id(self, value):
        if value is None:
            return None
        request = self.context["request"]
        try:
            return MembershipPlan.objects.for_organization(request.user.organization).get(uuid=value)
        except MembershipPlan.DoesNotExist:
            raise serializers.ValidationError("Plan not found in your organization.")

    def validate_assigned_staff_id(self, value):
        if value is None:
            return None
        request = self.context["request"]
        try:
            return User.objects.for_organization(request.user.organization).get(uuid=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Staff user not found in your organization.")

    def create(self, validated_data):
        request = self.context["request"]
        branch = validated_data.pop("branch_id")
        plan = validated_data.pop("interested_plan_id", None)
        staff = validated_data.pop("assigned_staff_id", None)
        if request.user.role == "TRAINER":
            staff = request.user
        lead = Lead(
            organization=request.user.organization,
            branch=branch,
            interested_plan=plan,
            assigned_staff=staff,
            **validated_data,
        )
        lead.full_clean()
        lead.save()
        return lead


class LeadActivitySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    created_by_id = serializers.SerializerMethodField()

    class Meta:
        model = LeadActivity
        fields = ["id", "activity_type", "notes", "created_by_id", "created_at"]
        read_only_fields = fields

    def get_created_by_id(self, obj):
        return str(obj.created_by.uuid) if obj.created_by_id else None


class LeadActivityWriteSerializer(serializers.Serializer):
    activity_type = serializers.CharField(max_length=100)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
