"""Local development settings (docker-compose)."""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Local filesystem storage for uploads in dev (S3 in staging/production —
# DEC-014). Keeps local dev independent of AWS credentials.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
