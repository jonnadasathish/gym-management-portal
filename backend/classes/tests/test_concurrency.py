"""Threaded last-seat booking tests (AGENTS.md §23.2 / §59.7).

`transaction=True` is required so worker threads see committed factory rows
under MySQL; pytest-django's default test transaction is invisible to them.
"""

import threading

import pytest

from classes.models import Booking
from classes.services import BookingError, book_occurrence
from classes.tests.factories import ClassOccurrenceFactory, GymClassFactory
from members.models import Member
from members.tests.factories import MemberFactory

pytestmark = pytest.mark.django_db(transaction=True)


def test_last_seat_booking_never_exceeds_capacity():
    gym_class = GymClassFactory(capacity=1)
    occurrence = ClassOccurrenceFactory(gym_class=gym_class, organization=gym_class.organization)
    members = [
        MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch),
        MemberFactory(organization=gym_class.organization, home_branch=gym_class.branch),
    ]
    occurrence_id = occurrence.id
    member_ids = [member.id for member in members]
    capacity = occurrence.effective_capacity
    assert capacity == 1

    barrier = threading.Barrier(2)
    lock = threading.Lock()
    outcomes = []

    def worker(member_id):
        from django.db import connection

        try:
            barrier.wait(timeout=10)
            member = Member.objects.get(pk=member_id)
            booking = book_occurrence(occurrence_id=occurrence_id, member=member)
            with lock:
                outcomes.append(("ok", booking.status))
        except BookingError as exc:
            with lock:
                outcomes.append(("error", exc.code))
        except Exception as exc:
            with lock:
                outcomes.append(("unexpected", f"{type(exc).__name__}: {exc}"))
        finally:
            connection.close()

    threads = [threading.Thread(target=worker, args=(member_id,)) for member_id in member_ids]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive(), "booking worker did not finish"

    successes = [item for item in outcomes if item[0] == "ok"]
    class_full = [item for item in outcomes if item[0] == "error" and item[1] == "CLASS_FULL"]
    unexpected = [item for item in outcomes if item[0] == "unexpected"]
    assert not unexpected, unexpected
    assert len(successes) == 1
    assert len(class_full) == 1
    assert successes[0][1] == Booking.Status.BOOKED

    booked = Booking.objects.filter(occurrence_id=occurrence_id, status=Booking.Status.BOOKED).count()
    assert booked == 1
    assert booked <= capacity
