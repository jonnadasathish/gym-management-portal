import pytest

from accounts.tests.factories import OwnerFactory
from branches.tests.factories import BranchFactory
from data_migration.models import ImportJob
from data_migration.services import confirm_import, preview_members_csv
from data_migration.tests.factories import ImportJobFactory
from members.models import Member

pytestmark = pytest.mark.django_db


def test_preview_phone_missing_has_errors_and_confirm_does_not_create():
    owner = OwnerFactory()
    BranchFactory(organization=owner.organization, name="Andheri")
    job = ImportJobFactory(
        organization=owner.organization,
        uploaded_by=owner,
        raw_csv="full_name,phone,home_branch_name,joining_date\nAnita Rao,,Andheri,2026-09-28\n",
    )
    before = Member.objects.for_organization(owner.organization).count()

    preview_members_csv(job)
    job.refresh_from_db()
    assert job.status == ImportJob.Status.PREVIEW_READY
    assert job.error_rows >= 1
    assert job.valid_rows == 0
    assert job.row_errors.count() >= 1
    assert Member.objects.for_organization(owner.organization).count() == before

    confirm_import(job)
    job.refresh_from_db()
    assert job.status == ImportJob.Status.COMPLETED
    assert Member.objects.for_organization(owner.organization).count() == before
    assert not Member.objects.for_organization(owner.organization).filter(full_name="Anita Rao").exists()


def test_valid_preview_and_confirm_creates_one_member():
    owner = OwnerFactory()
    branch = BranchFactory(organization=owner.organization, name="Andheri")
    job = ImportJobFactory(
        organization=owner.organization,
        uploaded_by=owner,
        raw_csv="full_name,phone,home_branch_name,joining_date\nAnita Rao,+919876509910,Andheri,2026-09-28\n",
    )
    before = Member.objects.for_organization(owner.organization).count()

    preview_members_csv(job)
    job.refresh_from_db()
    assert job.status == ImportJob.Status.PREVIEW_READY
    assert job.error_rows == 0
    assert job.valid_rows == 1
    assert Member.objects.for_organization(owner.organization).count() == before

    confirm_import(job)
    members = Member.objects.for_organization(owner.organization)
    assert members.count() == before + 1
    member = members.get(phone="+919876509910")
    assert member.full_name == "Anita Rao"
    assert member.home_branch_id == branch.id
    assert member.organization_id == owner.organization_id
    assert member.member_code.startswith("GYM-")
