from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from pt.models import PTSession
from pt.services import PTStateError, cancel_session, complete_session, reschedule_session, schedule_session
from pt.tests.factories import PTPackageFactory, PTSessionFactory

pytestmark = pytest.mark.django_db


def test_complete_decrements_balance_once():
    package = PTPackageFactory(sessions_purchased=2, sessions_consumed=0)
    session = PTSessionFactory(package=package, member=package.member, trainer=package.trainer, organization=package.organization)
    complete_session(session_id=session.id)
    package.refresh_from_db()
    session.refresh_from_db()
    assert session.status == PTSession.Status.COMPLETED
    assert package.sessions_consumed == 1
    with pytest.raises(PTStateError):
        complete_session(session_id=session.id)
    package.refresh_from_db()
    assert package.sessions_consumed == 1


def test_cancel_does_not_decrement_balance():
    package = PTPackageFactory(sessions_purchased=5, sessions_consumed=1)
    session = PTSessionFactory(package=package, member=package.member, trainer=package.trainer, organization=package.organization)
    cancel_session(session_id=session.id)
    package.refresh_from_db()
    assert package.sessions_consumed == 1
    session.refresh_from_db()
    assert session.status == PTSession.Status.CANCELLED


def test_cannot_complete_beyond_purchased():
    package = PTPackageFactory(sessions_purchased=1, sessions_consumed=1)
    session = PTSessionFactory(package=package, member=package.member, trainer=package.trainer, organization=package.organization)
    with pytest.raises(PTStateError) as exc:
        complete_session(session_id=session.id)
    assert exc.value.code == "NO_SESSIONS_REMAINING"


def test_schedule_rejects_member_overlap():
    package = PTPackageFactory()
    start = timezone.now() + timedelta(days=2)
    schedule_session(package_id=package.id, scheduled_at=start, duration_minutes=60)
    with pytest.raises(PTStateError) as exc:
        schedule_session(package_id=package.id, scheduled_at=start + timedelta(minutes=15), duration_minutes=60)
    assert exc.value.code == "MEMBER_OVERLAP"


def test_reschedule_updates_same_row_and_stays_scheduled():
    package = PTPackageFactory()
    start = timezone.now() + timedelta(days=2)
    session = schedule_session(package_id=package.id, scheduled_at=start, duration_minutes=60)
    new_start = start + timedelta(days=1)
    updated = reschedule_session(session_id=session.id, scheduled_at=new_start, duration_minutes=45)
    session.refresh_from_db()
    assert updated.id == session.id
    assert session.status == PTSession.Status.SCHEDULED
    assert session.scheduled_at == new_start
    assert session.duration_minutes == 45
    assert PTSession.objects.filter(package=package).count() == 1


def test_reschedule_rejects_member_overlap():
    package = PTPackageFactory()
    start = timezone.now() + timedelta(days=2)
    schedule_session(package_id=package.id, scheduled_at=start, duration_minutes=60)
    later = schedule_session(package_id=package.id, scheduled_at=start + timedelta(hours=3), duration_minutes=60)
    with pytest.raises(PTStateError) as exc:
        reschedule_session(session_id=later.id, scheduled_at=start + timedelta(minutes=15))
    assert exc.value.code == "MEMBER_OVERLAP"
    later.refresh_from_db()
    assert later.scheduled_at == start + timedelta(hours=3)
    assert later.status == PTSession.Status.SCHEDULED


def test_cannot_reschedule_completed():
    package = PTPackageFactory()
    session = PTSessionFactory(package=package, member=package.member, trainer=package.trainer, organization=package.organization)
    complete_session(session_id=session.id)
    with pytest.raises(PTStateError) as exc:
        reschedule_session(session_id=session.id, scheduled_at=timezone.now() + timedelta(days=3))
    assert exc.value.code == "INVALID_STATUS"
    session.refresh_from_db()
    assert session.status == PTSession.Status.COMPLETED
