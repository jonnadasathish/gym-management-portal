from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ImportJobViewSet

app_name = "data_migration"

router = DefaultRouter()
router.register("jobs", ImportJobViewSet, basename="import-job")

urlpatterns = [path("", include(router.urls))]
