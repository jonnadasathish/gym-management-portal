"""Mandatory tenant-isolation coverage for memberships.Membership /
MembershipPlan (AGENTS.md §16.4)."""

import pytest

from memberships.models import FreezeRequest, Membership, MembershipPlan
from memberships.tests.factories import FreezeRequestFactory, MembershipFactory, MembershipPlanFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_membership_plans_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    plan_a = MembershipPlanFactory(organization=org_a)
    plan_b = MembershipPlanFactory(organization=org_b)

    visible = MembershipPlan.objects.for_organization(org_a)
    assert plan_a in visible
    assert plan_b not in visible


def test_memberships_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    from members.tests.factories import MemberFactory

    membership_a = MembershipFactory(member=MemberFactory(organization=org_a))
    membership_b = MembershipFactory(member=MemberFactory(organization=org_b))

    visible = Membership.objects.for_organization(org_a)
    assert membership_a in visible
    assert membership_b not in visible


def test_freeze_requests_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    from members.tests.factories import MemberFactory

    request_a = FreezeRequestFactory(membership=MembershipFactory(member=MemberFactory(organization=org_a)))
    request_b = FreezeRequestFactory(membership=MembershipFactory(member=MemberFactory(organization=org_b)))

    visible = FreezeRequest.objects.for_organization(org_a)
    assert request_a in visible
    assert request_b not in visible
