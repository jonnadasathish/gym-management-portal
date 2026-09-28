"""CSV import jobs. Preview never writes Member rows; confirm imports valid rows only."""

from django.db import models

from core.models import TenantScopedModel


class ImportJob(TenantScopedModel):
    class EntityType(models.TextChoices):
        MEMBERS = "MEMBERS", "Members"

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PREVIEW_READY = "PREVIEW_READY", "Preview ready"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    uploaded_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="import_jobs"
    )
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    raw_csv = models.TextField()
    total_rows = models.PositiveIntegerField(default=0)
    valid_rows = models.PositiveIntegerField(default=0)
    error_rows = models.PositiveIntegerField(default=0)
    report = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "status"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.entity_type} ({self.status})"


class ImportRowError(models.Model):
    job = models.ForeignKey(ImportJob, on_delete=models.CASCADE, related_name="row_errors")
    row_number = models.PositiveIntegerField()
    raw_data = models.JSONField(default=dict)
    error_messages = models.JSONField(default=list)

    class Meta:
        ordering = ["row_number"]

    def __str__(self):
        return f"row {self.row_number} ({self.job_id})"
