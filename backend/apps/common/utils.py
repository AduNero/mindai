def get_client_ip(request):
    """
    Resolve the real client IP, honoring X-Forwarded-For when the app sits
    behind the Nginx reverse proxy (see docker/nginx). Falls back to
    REMOTE_ADDR for direct connections (e.g. local development).
    """

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")[:500]
