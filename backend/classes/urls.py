from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, ClassOccurrenceViewSet, GymClassViewSet, TrainerListView

app_name = "gym_classes"

router = DefaultRouter()
router.register("catalog", GymClassViewSet, basename="gym-class")
router.register("occurrences", ClassOccurrenceViewSet, basename="occurrence")
router.register("bookings", BookingViewSet, basename="booking")
router.register("trainers", TrainerListView, basename="trainer")

urlpatterns = [path("", include(router.urls))]
