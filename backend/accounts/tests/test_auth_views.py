"""API-level tests for the DEC-010 JWT auth flow: login sets an httpOnly
refresh cookie and returns an access token in the body; refresh rotates the
cookie; logout blacklists it; /me/ requires a valid access token.
"""

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory(email="staff@example.com", password="StrongPass123!")


def test_login_returns_access_token_and_sets_httponly_refresh_cookie(user):
    client = APIClient()
    response = client.post(reverse("accounts:login"), {"email": user.email, "password": "StrongPass123!"})

    assert response.status_code == 200
    assert "access" in response.data["data"]
    assert response.data["data"]["user"]["email"] == user.email

    cookie = response.cookies.get(settings.JWT_REFRESH_COOKIE_NAME)
    assert cookie is not None
    assert cookie["httponly"] is True
    # simplejwt/http.cookies renders samesite lower-cased key
    assert cookie["samesite"] == settings.JWT_REFRESH_COOKIE_SAMESITE


def test_login_with_wrong_password_returns_401(user):
    client = APIClient()
    response = client.post(reverse("accounts:login"), {"email": user.email, "password": "wrong"})
    assert response.status_code == 401
    assert response.data["error"]["code"] == "AUTHENTICATION_FAILED"


def test_login_sixth_attempt_in_burst_returns_429(user):
    client = APIClient()
    url = reverse("accounts:login")
    payload = {"email": user.email, "password": "wrong"}

    statuses = [client.post(url, payload).status_code for _ in range(5)]
    assert statuses == [401, 401, 401, 401, 401]

    sixth = client.post(url, payload)
    assert sixth.status_code == 429
    assert sixth.data["error"]["code"] == "RATE_LIMITED"


def test_me_requires_authentication():
    client = APIClient()
    response = client.get(reverse("accounts:me"))
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_access_token(user):
    client = APIClient()
    login_response = client.post(reverse("accounts:login"), {"email": user.email, "password": "StrongPass123!"})
    access = login_response.data["data"]["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = client.get(reverse("accounts:me"))

    assert response.status_code == 200
    assert response.data["data"]["email"] == user.email
    assert response.data["data"]["id"] == str(user.uuid)


def test_refresh_rotates_cookie_and_returns_new_access_token(user):
    client = APIClient()
    login_response = client.post(reverse("accounts:login"), {"email": user.email, "password": "StrongPass123!"})
    old_refresh_cookie = login_response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value

    client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = old_refresh_cookie
    refresh_response = client.post(reverse("accounts:refresh"))

    assert refresh_response.status_code == 200
    assert "access" in refresh_response.data["data"]
    new_refresh_cookie = refresh_response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
    assert new_refresh_cookie != old_refresh_cookie


def test_refresh_without_cookie_returns_401():
    client = APIClient()
    response = client.post(reverse("accounts:refresh"))
    assert response.status_code == 401


def test_logout_blacklists_refresh_token(user):
    client = APIClient()
    login_response = client.post(reverse("accounts:login"), {"email": user.email, "password": "StrongPass123!"})
    access = login_response.data["data"]["access"]
    refresh_cookie = login_response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = refresh_cookie
    logout_response = client.post(reverse("accounts:logout"))
    assert logout_response.status_code == 204

    # Using the same (now-blacklisted) refresh cookie again must fail.
    client2 = APIClient()
    client2.cookies[settings.JWT_REFRESH_COOKIE_NAME] = refresh_cookie
    reuse_response = client2.post(reverse("accounts:refresh"))
    assert reuse_response.status_code == 401
