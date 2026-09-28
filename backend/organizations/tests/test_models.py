import pytest

from organizations.models import Organization
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_organization_created_with_defaults():
    org = OrganizationFactory()
    assert org.status == Organization.Status.ACTIVE
    assert org.default_currency == "INR"
    assert org.default_timezone == "Asia/Kolkata"
    assert org.uuid is not None


def test_organization_str_is_name():
    org = OrganizationFactory(name="Iron Paradise")
    assert str(org) == "Iron Paradise"
