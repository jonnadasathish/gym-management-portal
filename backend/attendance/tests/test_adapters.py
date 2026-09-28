from datetime import datetime, timezone

from attendance.adapters import AccessControlAdapter
from attendance.models import Attendance


class FakeAccessControlAdapter:
    def parse_event(self, payload):
        return {
            "member_external_id": payload["badge_id"],
            "device_id": payload["device_id"],
            "occurred_at": payload["occurred_at"],
        }

    def supports_method(self):
        return Attendance.Method.BIOMETRIC


def test_fake_access_control_adapter_parse_event():
    adapter = FakeAccessControlAdapter()
    assert isinstance(adapter, AccessControlAdapter)
    occurred_at = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
    result = adapter.parse_event(
        {
            "badge_id": "EXT-123",
            "device_id": "gate-1",
            "occurred_at": occurred_at,
        }
    )
    assert result == {
        "member_external_id": "EXT-123",
        "device_id": "gate-1",
        "occurred_at": occurred_at,
    }
    assert adapter.supports_method() == Attendance.Method.BIOMETRIC
