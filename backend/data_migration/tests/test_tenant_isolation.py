"""Mandatory tenant-isolation coverage for data_migration.ImportJob (AGENTS.md §16.4)."""

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from core.tests.api import auth_client
from data_migration.models import ImportJob
from data_migration.tests.factories import ImportJobFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_import_jobs_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    job_a = ImportJobFactory(organization=org_a)
    job_b = ImportJobFactory(organization=org_b)

    visible = ImportJob.objects.for_organization(org_a)
    assert job_a in visible
    assert job_b not in visible


def test_other_org_cannot_see_import_job():
    owner = OwnerFactory()
    job = ImportJobFactory()
    response = auth_client(owner).get(f"/api/v1/data-migration/jobs/{job.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
