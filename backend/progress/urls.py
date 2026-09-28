from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PersonalBestViewSet, ProgressEntryViewSet

app_name = "progress"

router = DefaultRouter()
router.register("entries", ProgressEntryViewSet, basename="progress-entry")
router.register("personal-bests", PersonalBestViewSet, basename="personal-best")

urlpatterns = [path("", include(router.urls))]
