import pytest
from django.db import IntegrityError, transaction

from accounts.tests.factories import UserFactory
from branches.models import BranchAccess
from branches.tests.factories import BranchFactory

pytestmark = pytest.mark.django_db


def test_branch_access_grant_created():
    user = UserFactory()
    other_branch = BranchFactory(organization=user.organization)
    grant = BranchAccess.objects.create(user=user, branch=other_branch, granted_by=user)
    assert grant.branch == other_branch


def test_duplicate_branch_access_grant_is_rejected():
    user = UserFactory()
    other_branch = BranchFactory(organization=user.organization)
    BranchAccess.objects.create(user=user, branch=other_branch)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            BranchAccess.objects.create(user=user, branch=other_branch)
