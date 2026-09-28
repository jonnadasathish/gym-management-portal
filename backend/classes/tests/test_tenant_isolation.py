import pytest

from classes.models import GymClass
from classes.tests.factories import GymClassFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_classes_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    class_a = GymClassFactory(branch__organization=org_a, organization=org_a)
    class_b = GymClassFactory(branch__organization=org_b, organization=org_b)
    visible = GymClass.objects.for_organization(org_a)
    assert class_a in visible
    assert class_b not in visible
