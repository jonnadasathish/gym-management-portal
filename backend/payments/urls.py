from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, RazorpayWebhookView, SubscriptionViewSet

app_name = "payments"

subscription_router = DefaultRouter()
subscription_router.register("", SubscriptionViewSet, basename="subscription")

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path("webhooks/razorpay/", RazorpayWebhookView.as_view(), name="razorpay-webhook"),
    path("subscriptions/", include(subscription_router.urls)),
    path("", include(router.urls)),
]
