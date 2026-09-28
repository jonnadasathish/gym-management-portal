"""Threaded PT completion tests (AGENTS.md §24.2 / §59.10).

`transaction=True` is required so worker threads see committed factory rows
under MySQL; pytest-django's default test transaction is invisible to them.
"""

import threading

import pytest

from pt.models import PTSession
from pt.services import PTStateError, complete_session
from pt.tests.factories import PTPackageFactory, PTSessionFactory

pytestmark = pytest.mark.django_db(transaction=True)


def test_concurrent_complete_session_consumes_balance_once():
    package = PTPackageFactory(sessions_purchased=5, sessions_consumed=0)
    session = PTSessionFactory(
        package=package,
        member=package.member,
        trainer=package.trainer,
        organization=package.organization,
        status=PTSession.Status.SCHEDULED,
    )
    session_id = session.id

    barrier = threading.Barrier(2)
    lock = threading.Lock()
    outcomes = []

    def worker():
        from django.db import connection

        try:
            barrier.wait(timeout=10)
            complete_session(session_id=session_id)
            with lock:
                outcomes.append(("ok", None))
        except PTStateError as exc:
            with lock:
                outcomes.append(("error", exc.code))
        except Exception as exc:
            with lock:
                outcomes.append(("unexpected", f"{type(exc).__name__}: {exc}"))
        finally:
            connection.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive(), "complete_session worker did not finish"

    successes = [item for item in outcomes if item[0] == "ok"]
    state_errors = [item for item in outcomes if item[0] == "error"]
    unexpected = [item for item in outcomes if item[0] == "unexpected"]
    assert not unexpected, unexpected
    assert len(successes) == 1
    assert len(state_errors) == 1

    package.refresh_from_db()
    session.refresh_from_db()
    assert package.sessions_consumed == 1
    assert session.status == PTSession.Status.COMPLETED
