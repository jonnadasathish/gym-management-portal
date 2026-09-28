from rest_framework import serializers


class BranchRevenueSerializer(serializers.Serializer):
    branch_id = serializers.CharField()
    branch_name = serializers.CharField()
    monthly_collection = serializers.DecimalField(max_digits=12, decimal_places=2)


class RevenueMetricsSerializer(serializers.Serializer):
    today_collection = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_collection = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_dues = serializers.DecimalField(max_digits=12, decimal_places=2)
    refunds_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    by_branch = BranchRevenueSerializer(many=True)


class MembershipMetricsSerializer(serializers.Serializer):
    active = serializers.IntegerField()
    expired = serializers.IntegerField()
    expiring_7 = serializers.IntegerField()
    expiring_30 = serializers.IntegerField()
    new_month = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    frozen = serializers.IntegerField()


class AttendanceMetricsSerializer(serializers.Serializer):
    today_checkins = serializers.IntegerField()


class PTMetricsSerializer(serializers.Serializer):
    scheduled_sessions = serializers.IntegerField()
    completed_sessions = serializers.IntegerField()
    remaining_package_sessions = serializers.IntegerField()


class OwnerDashboardSerializer(serializers.Serializer):
    revenue = RevenueMetricsSerializer()
    membership = MembershipMetricsSerializer()
    attendance = AttendanceMetricsSerializer()
    pt = PTMetricsSerializer()
