"""Member CSV preview/confirm. Preview never creates Member rows (AGENTS.md §31)."""

import csv
import io
from collections import Counter
from datetime import date

from django.db import transaction
from django.utils import timezone

from branches.models import Branch
from data_migration.models import ImportJob, ImportRowError
from members.models import Member


class MigrationStateError(Exception):
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


def _normalize_row(row):
    return {(k or "").strip(): (v.strip() if isinstance(v, str) else v) or "" for k, v in row.items()}


def _validate_member_rows(job):
    text = (job.raw_csv or "").lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text))
    raw_rows = [_normalize_row(row) for row in reader]

    phone_counts = Counter(row.get("phone", "") for row in raw_rows if row.get("phone"))
    existing_phones = set(
        Member.objects.for_organization(job.organization).values_list("phone", flat=True)
    )
    branches_by_name = {}
    for branch in Branch.objects.for_organization(job.organization):
        branches_by_name.setdefault(branch.name, []).append(branch)

    parsed = []
    for index, raw in enumerate(raw_rows, start=2):
        errors = []
        full_name = raw.get("full_name", "")
        phone = raw.get("phone", "")
        home_branch_name = raw.get("home_branch_name", "")
        joining_raw = raw.get("joining_date", "")

        if not full_name:
            errors.append("full_name is required.")
        if not phone:
            errors.append("phone is required.")
        elif phone_counts[phone] > 1:
            errors.append("Duplicate phone in this file.")
        elif phone in existing_phones:
            errors.append("Phone already exists in this organization.")

        home_branch = None
        if not home_branch_name:
            errors.append("home_branch_name is required.")
        else:
            matches = branches_by_name.get(home_branch_name, [])
            if not matches:
                errors.append("Branch not found in your organization.")
            else:
                home_branch = matches[0]

        joining_date = None
        if joining_raw:
            try:
                joining_date = date.fromisoformat(joining_raw)
            except ValueError:
                errors.append("joining_date must be an ISO date (YYYY-MM-DD).")
        else:
            joining_date = timezone.localdate()

        validated = None
        if not errors:
            validated = {
                "full_name": full_name,
                "phone": phone,
                "home_branch": home_branch,
                "joining_date": joining_date,
            }
        parsed.append({"row_number": index, "raw": raw, "errors": errors, "validated": validated})
    return parsed


@transaction.atomic
def preview_members_csv(job):
    """Validate CSV and write ImportRowError rows. Never creates Member records."""
    job = ImportJob.objects.select_for_update().get(pk=job.pk)
    if job.entity_type != ImportJob.EntityType.MEMBERS:
        raise MigrationStateError("UNSUPPORTED_ENTITY", "Only MEMBERS import is supported in V1.")
    if job.status == ImportJob.Status.COMPLETED:
        raise MigrationStateError("INVALID_STATUS", "This import has already been completed.")

    parsed = _validate_member_rows(job)
    job.row_errors.all().delete()

    error_count = 0
    for row in parsed:
        if not row["errors"]:
            continue
        ImportRowError.objects.create(
            job=job,
            row_number=row["row_number"],
            raw_data=row["raw"],
            error_messages=row["errors"],
        )
        error_count += 1

    job.total_rows = len(parsed)
    job.error_rows = error_count
    job.valid_rows = job.total_rows - error_count
    job.status = ImportJob.Status.PREVIEW_READY
    job.report = {
        "total_rows": job.total_rows,
        "valid_rows": job.valid_rows,
        "error_rows": job.error_rows,
    }
    job.save(update_fields=["total_rows", "valid_rows", "error_rows", "status", "report", "updated_at"])
    return job


@transaction.atomic
def confirm_import(job):
    """Create Members for valid rows only. Unvalidated rows are never inserted."""
    job = ImportJob.objects.select_for_update().get(pk=job.pk)
    if job.status != ImportJob.Status.PREVIEW_READY:
        raise MigrationStateError("INVALID_STATUS", "Import can only be confirmed from PREVIEW_READY.")
    if job.entity_type != ImportJob.EntityType.MEMBERS:
        raise MigrationStateError("UNSUPPORTED_ENTITY", "Only MEMBERS import is supported in V1.")

    parsed = _validate_member_rows(job)
    imported = 0
    for row in parsed:
        if row["errors"] or not row["validated"]:
            continue
        values = row["validated"]
        member = Member(
            organization=job.organization,
            full_name=values["full_name"],
            phone=values["phone"],
            home_branch=values["home_branch"],
            joining_date=values["joining_date"],
            member_code=_next_member_code(job.organization),
        )
        member.full_clean()
        member.save()
        imported += 1

    report = dict(job.report or {})
    report["imported"] = imported
    job.report = report
    job.status = ImportJob.Status.COMPLETED
    job.save(update_fields=["status", "report", "updated_at"])
    return job
