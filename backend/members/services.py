"""Member portal login provisioning (REQ-055)."""

from django.db import transaction

from accounts.models import User
from members.models import Member


class MemberPortalError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


@transaction.atomic
def provision_member_login(*, member, email, password):
    if member.user_id:
        raise MemberPortalError("ALREADY_PROVISIONED", "This member already has a portal login.")
    if User.objects.filter(email__iexact=email).exists():
        raise MemberPortalError("EMAIL_IN_USE", "That email is already used by another account.")

    user = User(
        organization=member.organization,
        home_branch=member.home_branch,
        email=email,
        full_name=member.full_name,
        phone=member.phone,
        role=User.Role.MEMBER,
        is_active=True,
    )
    user.set_password(password)
    user.full_clean()
    user.save()

    member.user = user
    if not member.email:
        member.email = email
    member.save(update_fields=["user", "email", "updated_at"])
    return member
