"""Mandatory tenant-isolation coverage for trainers.TrainerProfile (AGENTS.md §16.4)."""

import pytest
from rest_framework import status

from accounts.tests.factories import OwnerFactory
from core.tests.api import auth_client
from organizations.tests.factories import OrganizationFactory
from trainers.models import TrainerProfile
from trainers.tests.factories import TrainerProfileFactory

pytestmark = pytest.mark.django_db


def test_trainer_profiles_scoped_by_organization():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    profile_a = TrainerProfileFactory(user__organization=org_a, organization=org_a)
    profile_b = TrainerProfileFactory(user__organization=org_b, organization=org_b)

    visible = TrainerProfile.objects.for_organization(org_a)

    assert profile_a in visible
    assert profile_b not in visible


def test_organization_a_cannot_read_organization_b_trainer_profile_by_scoped_lookup():
    org_a = OrganizationFactory()
    org_b = OrganizationFactory()
    profile_b = TrainerProfileFactory(user__organization=org_b, organization=org_b)

    with pytest.raises(TrainerProfile.DoesNotExist):
        TrainerProfile.objects.for_organization(org_a).get(pk=profile_b.pk)


def test_other_org_cannot_see_trainer_profile_via_api():
    owner = OwnerFactory()
    other = TrainerProfileFactory()
    response = auth_client(owner).get(f"/api/v1/trainers/{other.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
