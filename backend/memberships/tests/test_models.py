import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from members.tests.factories import MemberFactory
from memberships.models import FreezeRequest, Membership
from memberships.tests.factories import MembershipFactory, MembershipPlanFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_membership_created_active_by_default():
    membership = MembershipFactory()
    assert membership.status == Membership.Status.ACTIVE


def test_membership_organization_must_match_member_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    member = MemberFactory(organization=org_a)
    plan = MembershipPlanFactory(organization=org_a)
    membership = Membership(
        organization=org_b,
        member=member,
        plan=plan,
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(days=30),
        price=Decimal("2000.00"),
    )
    with pytest.raises(ValidationError):
        membership.full_clean()


def test_end_date_cannot_be_before_start_date():
    member = MemberFactory()
    plan = MembershipPlanFactory(organization=member.organization)
    membership = Membership(
        organization=member.organization,
        member=member,
        plan=plan,
        start_date=datetime.date.today(),
        end_date=datetime.date.today() - datetime.timedelta(days=1),
        price=Decimal("2000.00"),
    )
    with pytest.raises(ValidationError):
        membership.full_clean()


def test_price_snapshot_survives_plan_price_change():
    plan = MembershipPlanFactory(price=Decimal("2000.00"))
    membership = MembershipFactory(plan=plan, price=Decimal("2000.00"))

    plan.price = Decimal("2500.00")
    plan.save()

    membership.refresh_from_db()
    assert membership.price == Decimal("2000.00")


def test_freeze_request_organization_must_match_membership_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    membership = MembershipFactory(member=MemberFactory(organization=org_a))
    from accounts.tests.factories import UserFactory

    requester = UserFactory(role="MEMBER", organization=org_a)
    freeze_request = FreezeRequest(
        organization=org_b,
        membership=membership,
        member=membership.member,
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(days=5),
        reason="Travel",
        requested_by=requester,
    )
    with pytest.raises(ValidationError):
        freeze_request.full_clean()


def test_freeze_request_member_must_match_membership_member():
    membership = MembershipFactory()
    other_member = MemberFactory(organization=membership.organization)
    from accounts.tests.factories import UserFactory

    requester = UserFactory(role="MEMBER", organization=membership.organization)
    freeze_request = FreezeRequest(
        organization=membership.organization,
        membership=membership,
        member=other_member,
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(days=5),
        reason="Travel",
        requested_by=requester,
    )
    with pytest.raises(ValidationError):
        freeze_request.full_clean()
