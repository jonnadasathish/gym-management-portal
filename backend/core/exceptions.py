"""Consistent error envelope for every API endpoint (DEC-015).

Never leaks stack traces, SQL, or internal identifiers to the client
(AGENTS.md §32.2). Unhandled 500s are logged with full detail server-side
but returned to the client as a generic, safe message.
"""

import logging

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("gymportal.api")

_DEFAULT_CODE = "ERROR"

_STATUS_CODE_MAP = {
    400: "VALIDATION_ERROR",
    401: "AUTHENTICATION_REQUIRED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "UNPROCESSABLE_ENTITY",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
}


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled exception -> log full detail server-side, return a safe
        # generic envelope to the client. Never leak exc internals.
        logger.exception("Unhandled exception in API view", exc_info=exc)
        return Response(
            {"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
            status=500,
        )

    code = _STATUS_CODE_MAP.get(response.status_code, _DEFAULT_CODE)
    detail = response.data

    field_errors = None
    message = "An error occurred."

    if isinstance(detail, dict):
        # DRF validation errors come back as {"field": ["msg", ...]}
        non_field = detail.pop("non_field_errors", None) or detail.pop("detail", None)
        if detail:
            field_errors = detail
        if non_field:
            message = non_field if isinstance(non_field, str) else str(non_field)
        elif field_errors:
            message = "Validation failed."
    elif isinstance(detail, list):
        message = "; ".join(str(item) for item in detail)
    else:
        message = str(detail)

    error_body = {"code": code, "message": message}
    if field_errors:
        error_body["field_errors"] = field_errors

    response.data = {"error": error_body}
    return response


class ConflictError(APIException):
    """Use for concurrency-losing requests (DEC-020) — e.g. class full by
    the time a lock was acquired, PT package balance exhausted."""

    status_code = 409
    default_detail = "The request conflicts with the current state of the resource."
    default_code = "conflict"
