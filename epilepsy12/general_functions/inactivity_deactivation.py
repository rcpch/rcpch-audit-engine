"""
Deactivation of user accounts after a prolonged period of inactivity.

Users who have not logged in for longer than
`settings.ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS` days are deactivated
the next time they attempt to log in. The message shown on the login page
tells them to contact the Epilepsy12 team to have their account reactivated.
"""

import logging
from datetime import timedelta

from django.apps import apps
from django.conf import settings
from django.utils import timezone

from .client_ip import get_client_ip

logger = logging.getLogger(__name__)

# Fallback contact address used in the login page message if
# SITE_CONTACT_EMAIL is not set
DEFAULT_CONTACT_EMAIL = "epilepsy12@rcpch.ac.uk"


def get_site_contact_email() -> str:
    return getattr(settings, "SITE_CONTACT_EMAIL", None) or DEFAULT_CONTACT_EMAIL


def get_inactivity_deactivation_message() -> str:
    """
    The message shown on the login page to users whose account has been
    deactivated due to inactivity.
    """
    return (
        "Your account has been deactivated due to inactivity. "
        f"Please contact the Epilepsy12 team at {get_site_contact_email()} "
        "to reactivate your account."
    )


def get_last_login_datetime(user):
    """
    The user's last login, falling back to the date their account was created
    if they have never logged in.
    """
    return user.last_login or user.date_joined


def get_last_activity_datetime(user):
    """
    The reference time for the inactivity deactivation check: the user's last
    login (or the date their account was created if they have never logged
    in), or the time they were last reactivated by an administrator, whichever
    is later. Reactivation restarts the clock so that a user reactivated by
    their lead clinician is not immediately re-deactivated at their next
    login attempt.
    """
    last_activity = get_last_login_datetime(user)

    if user.reactivated_at and user.reactivated_at > last_activity:
        last_activity = user.reactivated_at

    return last_activity


def is_inactive_beyond_deactivation_period(user) -> bool:
    """
    Whether the user has been inactive for longer than
    settings.ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS days.

    Superusers are never deactivated automatically, and a period of zero (or
    less) disables the check entirely.
    """
    if settings.ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS <= 0:
        return False

    if user.is_superuser:
        return False

    last_activity = get_last_activity_datetime(user)
    if last_activity is None:
        return False

    return timezone.now() - last_activity > timedelta(
        days=settings.ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS
    )


def deactivate_user_for_inactivity(user, request=None) -> None:
    """
    Deactivates the user. The message shown on the login page (see
    get_inactivity_deactivation_message) tells them to contact the Epilepsy12
    team to have their account reactivated.
    """
    user.is_active = False
    user.save()

    # The is_active change is also picked up by the user change signals
    # (logged as "Superuser or admin status changed"); this entry records
    # the reason explicitly.
    VisitActivity = apps.get_model("epilepsy12", "VisitActivity")
    VisitActivity.objects.create(
        epilepsy12user=user,
        activity=VisitActivity.ACCOUNT_DEACTIVATED_INACTIVITY,
        ip_address=get_client_ip(request),
        details=(
            "Account automatically deactivated due to inactivity: no login for more "
            f"than {settings.ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS} days. "
            f"Last login: {user.last_login or 'Never'}."
        ),
    )

    logger.warning(
        "User %s deactivated due to inactivity (last activity %s)",
        user.email,
        get_last_activity_datetime(user),
    )
