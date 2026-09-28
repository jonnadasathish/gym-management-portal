"""
Base Django settings for the Gym Management Portal.

Shared by all environments (dev/staging/production). Environment-specific
overrides live in dev.py / staging.py / production.py.

Architecture reference: PROJECT_CONTEXT.md §26-§30, DEC-007, DEC-008,
DEC-010, DEC-011, DEC-013, DEC-014, DEC-015, DEC-017.
"""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
# .env is for local development only and is gitignored (DEC-017). In
# staging/production, real environment variables are injected by the
# platform (ECS task definition / Secrets Manager) and no .env file exists.
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-local-dev-key-do-not-use-in-production")

DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])


# --------------------------------------------------------------------------
# Applications (DEC-007 — approved 20-app decomposition; Phase 0 apps only
# are wired in so far — core/accounts/organizations/branches. Business-domain
# apps are added to INSTALLED_APPS as each is scaffolded in its own bounded
# task, per AGENTS.md "one task at a time".)
# --------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
]

LOCAL_APPS = [
    "core",
    "accounts",
    "organizations",
    "branches",
    "members",
    "memberships",
    "attendance",
    "billing",
    "payments",
    "classes",
    "pt",
    "workouts",
    "progress",
    "audit",
    "reports",
    "notifications",
    "crm",
    "data_migration",
    "trainers",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gymportal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gymportal.wsgi.application"
ASGI_APPLICATION = "gymportal.asgi.application"


# --------------------------------------------------------------------------
# Database (MySQL — DEC-003). Credentials come from environment variables
# only, never hard-coded (AGENTS.md §36.1 / §47).
# --------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME", default="gymportal"),
        "USER": env("DB_USER", default="gymportal"),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --------------------------------------------------------------------------
# Internationalization — India/IST baseline (PRD §9.8)
# --------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# --------------------------------------------------------------------------
# Static / media files
# --------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# File storage: S3 in staging/production (DEC-014), local filesystem in dev.
# Overridden in staging.py / production.py.


# --------------------------------------------------------------------------
# Django REST Framework (DEC-015 API conventions)
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardPageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "EXCEPTION_HANDLER": "core.exceptions.api_exception_handler",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_THROTTLE_RATES": {
        "login": "5/min",
    },
}

# --------------------------------------------------------------------------
# JWT (DEC-010 — approved by user 2026-09-28). Access token short-lived,
# refresh token rotates + is blacklisted on rotation/logout. The frontend
# holds the access token in memory only and the refresh token in an
# httpOnly cookie set by our own auth views (NOT simplejwt's default
# response body — see accounts.views for the cookie-setting wrapper).
# --------------------------------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "uuid",
    "USER_ID_CLAIM": "user_uuid",
}

# Cookie the refresh token rides in (set/read manually in accounts.views,
# simplejwt does not do this natively).
JWT_REFRESH_COOKIE_NAME = "gymportal_refresh"
JWT_REFRESH_COOKIE_PATH = "/api/v1/auth/"
JWT_REFRESH_COOKIE_HTTPONLY = True
JWT_REFRESH_COOKIE_SAMESITE = "Lax"
# COOKIE_SECURE is forced True in staging/production (HTTPS-only there).
JWT_REFRESH_COOKIE_SECURE = env.bool("JWT_REFRESH_COOKIE_SECURE", default=False)


# --------------------------------------------------------------------------
# CORS — frontend on a separate subdomain (DEC-010), credentials allowed so
# the httpOnly refresh cookie can be sent.
# --------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:5173"])
CORS_ALLOW_CREDENTIALS = True


# --------------------------------------------------------------------------
# Razorpay (DEC-005 / DEC-018). Secrets come from the environment only.
# create_order / process_refund remain unexecuted against the real API
# until sandbox credentials are configured (GYM-008).
# --------------------------------------------------------------------------

RAZORPAY_KEY_ID = env("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = env("RAZORPAY_KEY_SECRET", default="")
RAZORPAY_WEBHOOK_SECRET = env("RAZORPAY_WEBHOOK_SECRET", default="")


# --------------------------------------------------------------------------
# Celery / Redis (DEC-013)
# --------------------------------------------------------------------------

CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "membership-expiring-reminders": {
        "task": "notifications.tasks.emit_membership_expiring_reminders_task",
        "schedule": timedelta(hours=6),
    },
    "class-reminders": {
        "task": "notifications.tasks.emit_class_reminders_task",
        "schedule": timedelta(hours=1),
    },
    "pt-reminders": {
        "task": "notifications.tasks.emit_pt_reminders_task",
        "schedule": timedelta(hours=1),
    },
    "membership-expired-reminders": {
        "task": "notifications.tasks.emit_membership_expired_reminders_task",
        "schedule": timedelta(hours=6),
    },
    "birthday-reminders": {
        "task": "notifications.tasks.emit_birthday_reminders_task",
        "schedule": timedelta(hours=6),
    },
}


# --------------------------------------------------------------------------
# Logging — structured enough to answer "what/where/which org/which
# request" per AGENTS.md §50, without leaking secrets/PII (§36.2).
# --------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s %(module)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}
