from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExerciseViewSet, WorkoutLogViewSet, WorkoutProgramViewSet

app_name = "workouts"

router = DefaultRouter()
router.register("exercises", ExerciseViewSet, basename="exercise")
router.register("programs", WorkoutProgramViewSet, basename="program")
router.register("logs", WorkoutLogViewSet, basename="log")

urlpatterns = [path("", include(router.urls))]
