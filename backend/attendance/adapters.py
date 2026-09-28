"""Vendor-agnostic access-control adapter interface (REQ-068).

This is an interface only: no vendor HTTP clients, no invented device
protocols. A concrete adapter (biometric, RFID, or a test fake) normalizes
a payload into member_external_id / device_id / occurred_at. Check-in still
goes through `attendance.services.check_in` with Attendance.Method.BIOMETRIC.
"""

from __future__ import annotations

import uuid as uuid_lib
from datetime import datetime
from typing import Protocol, runtime_checkable

from attendance.models import Attendance
from attendance.services import AttendanceEligibilityError, check_in
from members.models import Member


@runtime_checkable
class AccessControlAdapter(Protocol):
    def parse_event(self, payload: dict) -> dict:
        """Normalize a device payload.

        Must return:
        - member_external_id: str
        - device_id: str
        - occurred_at: datetime
        """

    def supports_method(self) -> str:
        """Attendance method this adapter records (BIOMETRIC already exists)."""


def _resolve_member(organization, member_external_id):
    qs = Member.objects.for_organization(organization).alive()
    member = qs.filter(member_code=str(member_external_id)).first()
    if member is not None:
        return member
    try:
        external_uuid = uuid_lib.UUID(str(member_external_id))
    except (TypeError, ValueError):
        raise AttendanceEligibilityError(
            "MEMBER_NOT_FOUND",
            "No member matches this access-control identifier.",
        )
    member = qs.filter(uuid=external_uuid).first()
    if member is None:
        raise AttendanceEligibilityError(
            "MEMBER_NOT_FOUND",
            "No member matches this access-control identifier.",
        )
    return member


def check_in_from_adapter_event(*, organization, branch, adapter, payload, recorded_by=None):
    """Map an adapter event to a member and record BIOMETRIC check-in.

    `member_external_id` is resolved against Member.member_code, then
    Member.uuid. Method is Attendance.Method.BIOMETRIC (already on the enum).
    """

    event = adapter.parse_event(payload)
    member = _resolve_member(organization, event["member_external_id"])
    occurred_at = event.get("occurred_at")
    at = occurred_at if isinstance(occurred_at, datetime) else None
    return check_in(
        member=member,
        branch=branch,
        method=Attendance.Method.BIOMETRIC,
        device_id=event.get("device_id") or "",
        recorded_by=recorded_by,
        at=at,
    )
