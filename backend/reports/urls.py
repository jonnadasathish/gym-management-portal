from django.urls import path

from .views import OwnerDashboardCsvView, OwnerDashboardView, OwnerExpiredMembersCsvView

app_name = "reports"

urlpatterns = [
    path("dashboard/", OwnerDashboardView.as_view(), name="dashboard"),
    path("dashboard.csv", OwnerDashboardCsvView.as_view(), name="dashboard-csv"),
    path("expired-members.csv", OwnerExpiredMembersCsvView.as_view(), name="expired-members-csv"),
]
