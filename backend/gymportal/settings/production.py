"""Production settings — inherits staging's security posture, adds HSTS.

No AWS resources are provisioned by this file (OQ-009 remains open). This
is the target configuration for when infrastructure is actually stood up.
"""

from .staging import *  # noqa: F401,F403

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

if not ALLOWED_HOSTS:  # noqa: F405
    raise RuntimeError(
        "DJANGO_ALLOWED_HOSTS must be set explicitly in production — refusing "
        "to start with an empty allow-list."
    )
