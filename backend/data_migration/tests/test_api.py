import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from branches.tests.factories import BranchFactory
from core.tests.api import auth_client
from data_migration.models import ImportJob
from data_migration.tests.factories import ImportJobFactory
from members.models import Member

pytestmark = pytest.mark.django_db


def test_invalid_phone_missing_preview_has_errors_and_confirm_does_not_create():
    owner = OwnerFactory()
    BranchFactory(organization=owner.organization, name="Andheri")
    client = auth_client(owner)
    created = client.post(
        "/api/v1/data-migration/jobs/",
        {
            "raw_csv": "full_name,phone,home_branch_name,joining_date\nAnita Rao,,Andheri,2026-09-28\n",
            "entity_type": "MEMBERS",
        },
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED, created.data
    job_id = created.data["data"]["id"]
    before = Member.objects.for_organization(owner.organization).count()

    previewed = client.post(f"/api/v1/data-migration/jobs/{job_id}/preview/")
    assert previewed.status_code == status.HTTP_200_OK, previewed.data
    assert previewed.data["data"]["status"] == ImportJob.Status.PREVIEW_READY
    assert previewed.data["data"]["error_rows"] >= 1
    assert Member.objects.for_organization(owner.organization).count() == before

    confirmed = client.post(f"/api/v1/data-migration/jobs/{job_id}/confirm/")
    assert confirmed.status_code == status.HTTP_200_OK, confirmed.data
    assert Member.objects.for_organization(owner.organization).count() == before


def test_valid_preview_confirm_creates_one_member():
    owner = OwnerFactory()
    BranchFactory(organization=owner.organization, name="Andheri")
    client = auth_client(owner)
    created = client.post(
        "/api/v1/data-migration/jobs/",
        {
            "raw_csv": "full_name,phone,home_branch_name,joining_date\nAnita Rao,+919876509911,Andheri,2026-09-28\n",
            "entity_type": "MEMBERS",
        },
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED, created.data
    job_id = created.data["data"]["id"]
    before = Member.objects.for_organization(owner.organization).count()

    previewed = client.post(f"/api/v1/data-migration/jobs/{job_id}/preview/")
    assert previewed.status_code == status.HTTP_200_OK
    assert previewed.data["data"]["error_rows"] == 0
    assert Member.objects.for_organization(owner.organization).count() == before

    confirmed = client.post(f"/api/v1/data-migration/jobs/{job_id}/confirm/")
    assert confirmed.status_code == status.HTTP_200_OK
    assert confirmed.data["data"]["status"] == ImportJob.Status.COMPLETED
    members = Member.objects.for_organization(owner.organization)
    assert members.count() == before + 1
    assert members.get(phone="+919876509911").full_name == "Anita Rao"


def test_other_org_import_job_is_404():
    owner = OwnerFactory()
    job = ImportJobFactory()
    response = auth_client(owner).get(f"/api/v1/data-migration/jobs/{job.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
