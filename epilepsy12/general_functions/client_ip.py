def get_client_ip(request):
    """
    Extracts the client's IP address from the request object.
    Returns None if there is no request (eg authenticate() called without one,
    as by the Django test client or management commands)."""
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
