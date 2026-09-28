from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet

app_name = "crm"

router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")

urlpatterns = [path("", include(router.urls))]
