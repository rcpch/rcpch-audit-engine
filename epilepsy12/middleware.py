from datetime import datetime
import logging
from timeit import default_timer as timer
from threading import local
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

from epilepsy12.general_functions.entra_id import (
    ENTRA_ID_LOGIN_REQUIRED_MESSAGE,
    must_use_entra_id_login,
)
from epilepsy12.models import EntraIDDevice

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


class Epilepsy12CustomLoggingAttributesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            set_current_user(user)
        else:
            set_current_user(None)

        set_current_request(request)

        response = self.get_response(request)

        # Clean up thread-local storage after request
        if hasattr(_user, 'value'):
            delattr(_user, 'value')
        if hasattr(_user, 'request'):
            delattr(_user, 'request')

        return response


class Epilepsy12RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = timer()

        response = self.get_response(request)

        end = timer()

        duration = end - start
        duration_ms = round(duration * 1000)

        # The dev server already does request logging
        if settings.ENABLE_REQUEST_LOGGING:
            # This replaces the old gunicorn request logging which used this date format string
            gunicorn_formatted_datetime = (
                datetime.now().astimezone().strftime("%d/%m/%y:%H:%M:%S %z")
            )

            username_to_log = "-" if request.user.is_anonymous else request.user.email

            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
            method_path = f"{request.method} {request.get_full_path()}"
            content_length = response.get("Content-Length", "-")
            referer = request.META.get("HTTP_REFERER", "-")
            user_agent = request.META.get("HTTP_USER_AGENT", "-")

            log_message = (
                f"{x_forwarded_for} - {username_to_log} [{gunicorn_formatted_datetime}] "
                f'"{method_path}" {response.status_code} {content_length} '
                f'"{referer}" "{user_agent}" {duration_ms}'
            )

            request_logger.info(log_message)

        return response


class EntraIDLoginRequiredMiddleware:
    """
    When settings.ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF is True, end any
    session of a superuser or RCPCH Audit Team member that was not started by
    signing in with Microsoft Entra ID (for example one that began before the
    setting was switched on). Must come after django_otp's OTPMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF:
            user = getattr(request, "user", None)
            if (
                user is not None
                and user.is_authenticated
                and must_use_entra_id_login(user)
                and not isinstance(getattr(user, "otp_device", None), EntraIDDevice)
            ):
                logging.getLogger(__name__).info(
                    "Ending session for %s: must sign in with Entra ID", user.email
                )
                logout(request)
                messages.warning(request, ENTRA_ID_LOGIN_REQUIRED_MESSAGE)
                return redirect(settings.LOGIN_URL)

        return self.get_response(request)
