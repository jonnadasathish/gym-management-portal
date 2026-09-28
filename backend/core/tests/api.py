"""Shared API test helpers — JWT access token from an in-memory user."""

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def auth_client(user):
    client = APIClient()
    access = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client
