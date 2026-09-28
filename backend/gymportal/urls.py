"""URL configuration for gymportal project.

API namespace is `/api/v1/` (DEC-015). Business-domain URL groups are
added here as each app is scaffolded in its own bounded task.
"""

from django.contrib import admin
from django.urls import include, path

from core.views import liveness, readiness

urlpatterns = [
    path("healthz/", liveness, name="healthz"),
    path("readyz/", readiness, name="readyz"),
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/branches/", include("branches.urls")),
    path("api/v1/members/", include("members.urls")),
    path("api/v1/memberships/", include("memberships.urls")),
    path("api/v1/attendance/", include("attendance.urls")),
    path("api/v1/billing/", include("billing.urls")),
    path("api/v1/payments/", include("payments.urls")),
    path("api/v1/classes/", include("classes.urls")),
    path("api/v1/pt/", include("pt.urls")),
    path("api/v1/workouts/", include("workouts.urls")),
    path("api/v1/progress/", include("progress.urls")),
    path("api/v1/audit/", include("audit.urls")),
    path("api/v1/reports/", include("reports.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/crm/", include("crm.urls")),
    path("api/v1/data-migration/", include("data_migration.urls")),
    path("api/v1/trainers/", include("trainers.urls")),
]
