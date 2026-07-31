from apps.common.utils import get_client_ip, get_user_agent

from .context import get_current_request
from .models import AuditLog


def log_audit_event(action, user=None, request=None, model_name="", object_id="", **metadata):
    """
    Create an AuditLog entry. `request` may be passed explicitly (typical
    in views) or omitted to fall back to the thread-local request set by
    RequestContextMiddleware (useful from signal receivers / Celery tasks
    triggered synchronously within a request).
    """

    request = request or get_current_request()
    ip_address = get_client_ip(request) if request else None
    user_agent = get_user_agent(request) if request else ""

    return AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else "",
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata,
    )
