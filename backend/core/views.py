"""Unauthenticated process and dependency health probes (AGENTS.md §50).

Liveness (`/healthz/`) reports that the Django process can serve HTTP.
Readiness (`/readyz/`) reports MySQL and Redis availability. Probe
responses never include DSNs, passwords, or exception text.
"""

import logging

import redis
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger("gymportal.health")

_REDIS_SOCKET_TIMEOUT_SECONDS = 2


def _check_database():
    """Verify the default Django database connection can execute SQL."""
    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()


def _check_redis():
    """Ping Redis using the Celery broker URL (REDIS_URL)."""
    client = redis.from_url(
        settings.CELERY_BROKER_URL,
        socket_connect_timeout=_REDIS_SOCKET_TIMEOUT_SECONDS,
        socket_timeout=_REDIS_SOCKET_TIMEOUT_SECONDS,
    )
    try:
        if client.ping() is not True:
            raise ConnectionError("redis ping unsuccessful")
    finally:
        client.close()


def _run_check(name, checker):
    try:
        checker()
        return "ok"
    except Exception:
        logger.warning("Readiness check failed: %s", name)
        return "error"


@require_GET
def liveness(request):
    """Process is up. Does not touch MySQL or Redis."""
    return JsonResponse({"status": "ok"})


@require_GET
def readiness(request):
    """MySQL and Redis must both be reachable for a 200 response."""
    checks = {
        "database": _run_check("database", _check_database),
        "redis": _run_check("redis", _check_redis),
    }
    if all(value == "ok" for value in checks.values()):
        return JsonResponse({"status": "ok", "checks": checks})
    return JsonResponse(
        {"status": "unavailable", "checks": checks},
        status=503,
    )
