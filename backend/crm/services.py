"""Lead conversion. Creates a Member from name/phone/branch only — no extra fields."""

from django.db import transaction
from django.utils import timezone

from crm.models import Lead
from members.models import Member


class CRMStateError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def _next_member_code(organization):
    last = (
        Member.objects.filter(organization=organization, member_code__startswith="GYM-")
        .order_by("-id")
        .first()
    )
    if last and last.member_code.startswith("GYM-"):
        try:
            n = int(last.member_code.split("-", 1)[1]) + 1
        except ValueError:
            n = Member.objects.filter(organization=organization).count() + 1
    else:
        n = Member.objects.filter(organization=organization).count() + 1
    return f"GYM-{n:06d}"


@transaction.atomic
def convert_lead(*, lead_id):
    lead = Lead.objects.select_for_update().select_related("branch", "organization").get(pk=lead_id)
    if lead.status == Lead.Status.CONVERTED or lead.converted_member_id:
        raise CRMStateError("ALREADY_CONVERTED", "This lead has already been converted.")
    if Member.objects.filter(organization=lead.organization, phone=lead.phone).exists():
        raise CRMStateError("PHONE_IN_USE", "A member with this phone already exists in the organization.")

    member = Member(
        organization=lead.organization,
        full_name=lead.name,
        phone=lead.phone,
        home_branch=lead.branch,
        joining_date=timezone.localdate(),
        member_code=_next_member_code(lead.organization),
    )
    member.full_clean()
    member.save()

    lead.status = Lead.Status.CONVERTED
    lead.converted_member = member
    lead.save(update_fields=["status", "converted_member", "updated_at"])
    return lead, member
