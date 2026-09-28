import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_auth_throttle_cache():
    """Keep login ScopedRateThrottle counters isolated across tests."""
    cache.clear()
    yield
    cache.clear()
