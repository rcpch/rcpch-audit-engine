from datetime import datetime
import logging
from threading import local

from epilepsy12.models import Epilepsy12User

request_logger = logging.getLogger("epilepsy12_request_log")

_user = local()


def set_current_user(user):
    _user.value = user


def get_current_user():
    return getattr(_user, "value", None)


def set_current_request(request):
    """
    Store the current request in thread-local storage.
    """
    _user.request = request


def get_current_request():
    """
    Returns the current request object if available, otherwise None.
    This is useful for accessing the request in signals or other contexts.
    """
    try:
        return _user.request
    except AttributeError:
        return None


class Epilepsy12RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(getattr(request, "user", None))
        set_current_request(request)
        response = self.get_response(request)

        # The dev server already does request logging
        # if settings.ENABLE_REQUEST_LOGGING:
        # This replaces the old gunicorn request logging which used this format string
        # %({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"
        gunicorn_formatted_datetime = (
            datetime.now().astimezone().strftime("%d/%m/%y:%H:%M:%S %z")
        )

        user = get_current_user()

        username_to_log = user if user else "-"
        if user and hasattr(user, "email"):
            username_to_log = user.email

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        method_path = f"{request.method} {request.get_full_path()}"
        content_length = response.get("Content-Length", "-")
        referer = request.META.get("HTTP_REFERER", "-")
        user_agent = request.META.get("HTTP_USER_AGENT", "-")
        audit_year = request.session.get("selected_audit_year", "-")
        pz_code = request.session.get("pz_code", "-")

        log_message = (
            f"{x_forwarded_for} - {username_to_log} [{gunicorn_formatted_datetime}] "
            f'"{method_path}" {response.status_code} {content_length} '
            f'"{referer}" "{user_agent}" '
            f'audit_year="{audit_year}" pz_code="{pz_code}"'
        )
        request_logger.info(log_message)

        # Clean up thread-local storage after request
        if hasattr(_user, "value"):
            delattr(_user, "value")
        if hasattr(_user, "request"):
            delattr(_user, "request")

        return response
