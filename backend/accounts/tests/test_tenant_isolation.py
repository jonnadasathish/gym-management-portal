"""Mandatory tenant-isolation coverage for accounts.User (AGENTS.md §16.4)."""

import pytest

from accounts.models import User
from accounts.tests.factories import UserFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_users_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    user_a = UserFactory(organization=org_a)
    user_b = UserFactory(organization=org_b)

    org_a_users = User.objects.for_organization(org_a)

    assert user_a in org_a_users
    assert user_b not in org_a_users


def test_for_user_helper_uses_authenticated_users_own_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    requester = UserFactory(organization=org_a)
    UserFactory(organization=org_a)
    UserFactory(organization=org_b)

    visible = User.objects.for_user(requester)

    assert visible.count() == 2
    assert all(u.organization_id == org_a.id for u in visible)
