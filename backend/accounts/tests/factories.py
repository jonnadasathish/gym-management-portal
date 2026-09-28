import factory

from accounts.models import User
from branches.tests.factories import BranchFactory
from organizations.tests.factories import OrganizationFactory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    organization = factory.SubFactory(OrganizationFactory)
    home_branch = factory.SubFactory(BranchFactory, organization=factory.SelfAttribute("..organization"))
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Sequence(lambda n: f"Test User {n}")
    role = User.Role.STAFF_ADMIN
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or "TestPass123!")
        if create:
            obj.save()


class OwnerFactory(UserFactory):
    role = User.Role.OWNER
    home_branch = None
