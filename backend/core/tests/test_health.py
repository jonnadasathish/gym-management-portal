"""Liveness and readiness probes — unauthenticated, no secret leakage."""

from unittest.mock import patch

import pytest
from django.test import Client

_REDIS_SECRET = "redis-super-secret-password"


def test_healthz_returns_200():
    response = Client().get("/healthz/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_readyz_returns_200_when_dependencies_ok():
    response = Client().get("/readyz/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "checks": {"database": "ok", "redis": "ok"},
    }


@pytest.mark.django_db
def test_readyz_returns_503_when_redis_fails_without_leaking_secrets():
    def fail_redis():
        raise ConnectionError(
            f"Error 111 connecting to redis://:{_REDIS_SECRET}@localhost:6379/0"
        )

    with patch("core.views._check_redis", side_effect=fail_redis):
        response = Client().get("/readyz/")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["redis"] == "error"
    raw = response.content.decode()
    assert _REDIS_SECRET not in raw
    assert "redis://" not in raw
