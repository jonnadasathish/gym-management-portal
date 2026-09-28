import pytest

from organizations.tests.factories import OrganizationFactory
from pt.models import PTPackage
from pt.tests.factories import PTPackageFactory

pytestmark = pytest.mark.django_db


def test_pt_packages_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    pkg_a = PTPackageFactory(member__organization=org_a, organization=org_a)
    pkg_b = PTPackageFactory(member__organization=org_b, organization=org_b)
    visible = PTPackage.objects.for_organization(org_a)
    assert pkg_a in visible
    assert pkg_b not in visible
