"""Celery application (DEC-013 — Celery + Redis for async work: notification
delivery, large report generation, scheduled expiry scans, CSV import
processing)."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gymportal.settings.dev")

app = Celery("gymportal")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
