"""Staging settings — S3 storage, HTTPS-only cookies, no DEBUG.

Exact AWS sizing/topology is OQ-009 (still open, PROJECT_CONTEXT.md §28) —
this file only wires the *interfaces* (S3 backend, secure cookies) that were
approved in DEC-014/DEC-017; it does not provision any AWS resources.
"""

from .base import *  # noqa: F401,F403

DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)  # noqa: F405

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")  # noqa: F405
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="ap-south-1")  # noqa: F405
AWS_DEFAULT_ACL = None  # private bucket, presigned URLs only (DEC-014)
AWS_QUERYSTRING_AUTH = True
