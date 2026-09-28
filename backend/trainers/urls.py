from rest_framework.routers import DefaultRouter

from .views import TrainerProfileViewSet

app_name = "trainers"

router = DefaultRouter()
router.register("", TrainerProfileViewSet, basename="trainer")

urlpatterns = router.urls
