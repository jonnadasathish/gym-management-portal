from rest_framework.routers import DefaultRouter

from .views import MemberViewSet

app_name = "members"

router = DefaultRouter()
router.register("", MemberViewSet, basename="member")

urlpatterns = router.urls
