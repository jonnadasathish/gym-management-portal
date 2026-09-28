import pytest

from organizations.tests.factories import OrganizationFactory
from progress.models import PersonalBest, ProgressEntry
from progress.tests.factories import PersonalBestFactory, ProgressEntryFactory

pytestmark = pytest.mark.django_db


def test_progress_entries_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    entry_a = ProgressEntryFactory(member__organization=org_a, organization=org_a)
    entry_b = ProgressEntryFactory(member__organization=org_b, organization=org_b)
    visible = ProgressEntry.objects.for_organization(org_a)
    assert entry_a in visible
    assert entry_b not in visible


def test_personal_bests_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    pb_a = PersonalBestFactory(member__organization=org_a, organization=org_a)
    pb_b = PersonalBestFactory(member__organization=org_b, organization=org_b)
    visible = PersonalBest.objects.for_organization(org_a)
    assert pb_a in visible
    assert pb_b not in visible
