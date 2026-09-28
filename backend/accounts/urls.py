from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    RefreshView,
    StaffActivateView,
    StaffDeactivateView,
    StaffListView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("staff/", StaffListView.as_view(), name="staff"),
    path("staff/<uuid:uuid>/deactivate/", StaffDeactivateView.as_view(), name="staff-deactivate"),
    path("staff/<uuid:uuid>/activate/", StaffActivateView.as_view(), name="staff-activate"),
]
