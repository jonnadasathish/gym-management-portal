import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from accounts.tests.factories import UserFactory
from branches.tests.factories import BranchFactory
from members.models import Member
from members.tests.factories import MemberFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_member_created_with_defaults():
    member = MemberFactory()
    assert member.status == Member.Status.ACTIVE
    assert member.consent_status == Member.ConsentStatus.PENDING
    assert member.uuid is not None


def test_duplicate_phone_within_same_organization_is_rejected():
    org = OrganizationFactory()
    MemberFactory(organization=org, phone="+919876500001")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            MemberFactory(organization=org, phone="+919876500001")


def test_same_phone_allowed_across_different_organizations():
    member_a = MemberFactory(phone="+919876500002")
    member_b = MemberFactory(phone="+919876500002")
    assert member_a.organization_id != member_b.organization_id
    assert member_a.phone == member_b.phone


def test_assigned_trainer_must_have_trainer_role():
    org = OrganizationFactory()
    non_trainer = UserFactory(organization=org, role="STAFF_ADMIN")
    branch = BranchFactory(organization=org)
    member = Member(
        organization=org,
        home_branch=branch,
        assigned_trainer=non_trainer,
        member_code="GYM-000999",
        full_name="Test",
        phone="+919876500003",
        joining_date="2026-01-01",
    )
    with pytest.raises(ValidationError):
        member.full_clean()


def test_home_branch_must_belong_to_same_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    other_org_branch = BranchFactory(organization=org_b)
    member = Member(
        organization=org_a,
        home_branch=other_org_branch,
        member_code="GYM-000998",
        full_name="Test",
        phone="+919876500004",
        joining_date="2026-01-01",
    )
    with pytest.raises(ValidationError):
        member.full_clean()


def test_member_soft_delete():
    member = MemberFactory()
    member.soft_delete()
    assert member.is_deleted is True
    assert member.deleted_at is not None
    assert member not in Member.objects.alive()
