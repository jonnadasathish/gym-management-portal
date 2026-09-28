from django.contrib.auth.base_user import BaseUserManager

from core.models import TenantScopedQuerySet


class UserManager(BaseUserManager.from_queryset(TenantScopedQuerySet)):
    """`email` is the login identifier. NOTE (implementation refinement,
    recorded in PROJECT_CONTEXT.md GYM-005): email is enforced globally
    unique here, not merely per-organization as the original §27.A schema
    sketch said. Django's auth machinery (USERNAME_FIELD lookup,
    `authenticate()`) assumes a single global identity per credential, and
    the PRD's user stories never describe a "select your gym" login step.
    Per-organization-unique email with shared login would require a custom
    auth backend disambiguating by organization at login time, which is
    unnecessary complexity the PRD does not call for. Member.phone
    (REQ-022) is unaffected — that uniqueness is still per-organization.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "OWNER")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)
