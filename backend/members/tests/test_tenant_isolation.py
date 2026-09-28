"""Mandatory tenant-isolation coverage for members.Member (AGENTS.md §16.4)."""

import pytest

from members.models import Member
from members.tests.factories import MemberFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_members_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    member_a = MemberFactory(organization=org_a)
    member_b = MemberFactory(organization=org_b)

    visible = Member.objects.for_organization(org_a)

    assert member_a in visible
    assert member_b not in visible


def test_organization_a_cannot_read_organization_b_member_by_scoped_lookup():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    member_b = MemberFactory(organization=org_b)

    with pytest.raises(Member.DoesNotExist):
        Member.objects.for_organization(org_a).get(pk=member_b.pk)


def test_duplicate_phone_constraint_does_not_leak_across_organizations():
    """A phone number colliding in another org must not raise or block —
    proves the uniqueness constraint itself is correctly tenant-scoped and
    is not an accidental cross-tenant leak vector."""

    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    MemberFactory(organization=org_a, phone="+919999900000")
    # Must not raise:
    MemberFactory(organization=org_b, phone="+919999900000")
