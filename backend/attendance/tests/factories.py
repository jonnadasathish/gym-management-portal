import factory
from django.utils import timezone

from attendance.models import Attendance
from members.tests.factories import MemberFactory


class AttendanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attendance

    member = factory.SubFactory(MemberFactory)
    organization = factory.SelfAttribute("member.organization")
    branch = factory.SelfAttribute("member.home_branch")
    checkin_at = factory.LazyFunction(timezone.now)
    method = Attendance.Method.STAFF_SEARCH
