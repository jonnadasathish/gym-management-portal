from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationEmitView, NotificationLogViewSet, NotificationTemplateViewSet

app_name = "notifications"

router = DefaultRouter()
router.register("logs", NotificationLogViewSet, basename="log")
router.register("templates", NotificationTemplateViewSet, basename="template")

urlpatterns = [
    path("emit/", NotificationEmitView.as_view(), name="emit"),
    path("", include(router.urls)),
]
