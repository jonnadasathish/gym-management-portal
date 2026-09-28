from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PTPackageViewSet, PTSessionViewSet

app_name = "pt"

router = DefaultRouter()
router.register("packages", PTPackageViewSet, basename="package")
router.register("sessions", PTSessionViewSet, basename="session")

urlpatterns = [path("", include(router.urls))]
