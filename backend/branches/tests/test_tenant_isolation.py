"""Mandatory tenant-isolation coverage for a tenant-owned app (AGENTS.md
§16.4 / DEC-008). Proves organization A cannot read organization B's
branches through the model-layer scoping helper.
"""

import pytest

from branches.models import Branch
from branches.tests.factories import BranchFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_for_organization_only_returns_own_branches():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    branch_a = BranchFactory(organization=org_a)
    branch_b = BranchFactory(organization=org_b)

    org_a_branches = Branch.objects.for_organization(org_a)

    assert branch_a in org_a_branches
    assert branch_b not in org_a_branches
    assert org_a_branches.count() == 1


def test_organization_a_cannot_read_organization_b_branch_by_scoped_lookup():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    branch_b = BranchFactory(organization=org_b)

    with pytest.raises(Branch.DoesNotExist):
        Branch.objects.for_organization(org_a).get(pk=branch_b.pk)


def test_unscoped_manager_still_exists_for_admin_migrations_use(settings):
    """Documents the deliberate DEC-008 refinement: `.objects.all()` is not
    disabled outright (see core.models.TenantScopedManager docstring), but
    every application code path in views/services MUST use
    `for_user`/`for_organization` instead. This test exists so the
    refinement is verified, not merely asserted in a docstring."""

    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    BranchFactory(organization=org_a)
    BranchFactory(organization=org_b)

    assert Branch.objects.all().count() == 2
    assert Branch.objects.for_organization(org_a).count() == 1
