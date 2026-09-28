import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from accounts.tests.factories import OwnerFactory, UserFactory
from branches.tests.factories import BranchFactory
from organizations.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_user_created_with_hashed_password():
    user = UserFactory(password="MySecret123!")
    assert user.password != "MySecret123!"
    assert user.check_password("MySecret123!")


def test_owner_cannot_have_home_branch():
    org = OrganizationFactory()
    branch = BranchFactory(organization=org)
    user = User(
        organization=org,
        home_branch=branch,
        email="owner@example.com",
        full_name="Owner",
        role=User.Role.OWNER,
    )
    with pytest.raises(ValidationError):
        user.full_clean()


def test_staff_requires_home_branch():
    org = OrganizationFactory()
    user = User(
        organization=org,
        email="staff@example.com",
        full_name="Staff",
        role=User.Role.STAFF_ADMIN,
    )
    with pytest.raises(ValidationError):
        user.full_clean()


def test_owner_factory_has_no_home_branch():
    owner = OwnerFactory()
    assert owner.home_branch is None
    assert owner.role == User.Role.OWNER


def test_email_is_globally_unique():
    UserFactory(email="dup@example.com")
    with pytest.raises(Exception):
        UserFactory(email="dup@example.com")
