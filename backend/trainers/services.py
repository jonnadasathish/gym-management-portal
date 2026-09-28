"""Trainer compensation calculation (REQ-047). Read-only — never writes payroll rows.

REVENUE_SHARE does not invent a revenue base or PT revenue percentage.
"""

from decimal import Decimal

from classes.models import ClassOccurrence
from pt.models import PTSession

from .models import TrainerProfile

REVENUE_SHARE_NOTE = "Revenue share base is undefined; computed_amount is not calculated."


def calculate_compensation(*, trainer_user, start_date, end_date):
    """Return a compensation summary dict for [start_date, end_date] inclusive.

    Counts completed PT sessions and non-cancelled class occurrences in the
    trainer's organization only. Does not create or update any payroll records.
    """
    profile = trainer_user.trainer_profile
    org = trainer_user.organization
    completed_sessions = PTSession.objects.filter(
        organization=org,
        trainer=trainer_user,
        status=PTSession.Status.COMPLETED,
        scheduled_at__date__gte=start_date,
        scheduled_at__date__lte=end_date,
    ).count()
    classes_taught = (
        ClassOccurrence.objects.filter(
            organization=org,
            gym_class__trainer=trainer_user,
            start_time__date__gte=start_date,
            start_time__date__lte=end_date,
        )
        .exclude(status=ClassOccurrence.Status.CANCELLED)
        .count()
    )

    rate = profile.compensation_rate
    model = profile.compensation_model
    computed_amount = None
    note = None
    if model == TrainerProfile.CompensationModel.FIXED_SALARY:
        computed_amount = rate
    elif model == TrainerProfile.CompensationModel.PER_SESSION:
        computed_amount = Decimal(completed_sessions) * rate
    elif model == TrainerProfile.CompensationModel.PER_CLASS:
        computed_amount = Decimal(classes_taught) * rate
    elif model == TrainerProfile.CompensationModel.REVENUE_SHARE:
        computed_amount = None
        note = REVENUE_SHARE_NOTE

    result = {
        "trainer_id": trainer_user.uuid,
        "start_date": start_date,
        "end_date": end_date,
        "compensation_model": model,
        "compensation_rate": rate,
        "completed_sessions": completed_sessions,
        "classes_taught": classes_taught,
        "computed_amount": computed_amount,
    }
    if note is not None:
        result["note"] = note
    return result
