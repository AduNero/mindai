from .context import clear_current_request, set_current_request


class RequestContextMiddleware:
    """
    Stashes the current request in thread-local storage so that
    `apps.audit.utils.log_audit_event` can be called from places that
    don't have direct access to the request object (e.g. model signal
    receivers), while still resolving IP/user-agent for the audit trail.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        try:
            response = self.get_response(request)
        finally:
            clear_current_request()
        return response
