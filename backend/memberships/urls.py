from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FreezeRequestViewSet, MembershipPlanViewSet, MembershipViewSet

app_name = "memberships"

router = DefaultRouter()
router.register("plans", MembershipPlanViewSet, basename="plan")
router.register("freeze-requests", FreezeRequestViewSet, basename="freeze-request")
router.register("", MembershipViewSet, basename="membership")

urlpatterns = [
    path("", include(router.urls)),
]
