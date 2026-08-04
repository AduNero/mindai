import logging

from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("apps")


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handling to return a consistent error
    envelope: {"success": false, "error": {"code": ..., "message": ..., "details": ...}}
    instead of DRF's bare {"detail": ...} / field-keyed shape, so the
    frontend has one error-parsing code path for every endpoint.
    """

    response = drf_exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled exception in %s", context.get("view"))
        return response

    # DRF's ErrorDetail carries the `code=` passed to the exception (e.g.
    # AuthenticationFailed("...", code="email_not_verified")) — surfacing
    # it lets the frontend branch on a stable machine-readable reason
    # instead of matching on the (translatable, editable) message text.
    raw_detail = getattr(exc, "detail", None)
    reason_code = raw_detail.code if hasattr(raw_detail, "code") else None

    detail = response.data
    message = "Request failed."
    if isinstance(detail, dict) and "detail" in detail and len(detail) == 1:
        message = str(detail["detail"])
        details = {"code": reason_code} if reason_code else None
    else:
        details = detail
        if isinstance(detail, dict) and detail:
            first_value = next(iter(detail.values()))
            if isinstance(first_value, list) and first_value:
                message = str(first_value[0])

    response.data = {
        "success": False,
        "error": {
            "code": exc.__class__.__name__,
            "message": message,
            "details": details,
        },
    }
    return response
