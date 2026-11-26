"""
Sign in with Microsoft Entra ID (OAuth 2.0 authorisation code flow with PKCE,
via OpenID Connect).

Only superusers and RCPCH Audit Team members can sign in this way. Entra ID
applies RCPCH's own multi-factor authentication, so a successful sign in is
recorded against the user's EntraIDDevice and counts as a verified second
factor for the rest of the session.
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET
from django_otp import login as otp_login

from ..general_functions.client_ip import get_client_ip
from ..general_functions.entra_id import (
    build_entra_id_client,
    is_entra_id_email,
    may_use_entra_id_login,
)
from ..general_functions.inactivity_deactivation import (
    deactivate_user_for_inactivity,
    get_inactivity_deactivation_message,
    is_inactive_beyond_deactivation_period,
)
from ..models import EntraIDDevice, Epilepsy12User, VisitActivity
from .user_management_views import add_post_login_messages, get_post_login_url

logger = logging.getLogger(__name__)

ENTRA_ID_FLOW_SESSION_KEY = "entra_id_auth_code_flow"
ENTRA_ID_NEXT_SESSION_KEY = "entra_id_next"
ENTRA_ID_DEVICE_NAME = "Entra ID"

GENERIC_FAILURE_MESSAGE = (
    "Sign in with Microsoft failed. Please try again or contact the Epilepsy12 team."
)


def _redirect_uri(request):
    return request.build_absolute_uri(reverse("entra_id_callback"))


def _fail(request, message, user=None, details=None):
    """Show the user why sign in failed and audit it against their account."""
    if user is not None:
        VisitActivity.objects.create(
            activity=VisitActivity.UNSUCCESSFUL_LOGIN,
            ip_address=get_client_ip(request),
            epilepsy12user=user,
            details=f"Microsoft Entra ID sign in failed: {details or message}",
        )
    # error, not warning, so that it is emailed to the admins
    logger.error(
        "Entra ID sign in failed from %s for %s: %s",
        get_client_ip(request),
        user.email if user else "unmatched account",
        details or message,
    )
    messages.error(request, message)
    return redirect(settings.LOGIN_URL)


@require_GET
def entra_id_login(request):
    """Start the sign in: send the browser to Microsoft."""
    if not settings.ENTRA_ID_LOGIN_ENABLED:
        raise Http404()

    # Pre-select the account the user typed on the login page. Only addresses
    # on the Entra ID domain are passed on to Microsoft.
    login_hint = request.GET.get("login_hint", "").strip().lower()
    if is_entra_id_email(login_hint):
        account_selection = {"login_hint": login_hint}
    else:
        account_selection = {"prompt": "select_account"}

    flow = build_entra_id_client().initiate_auth_code_flow(
        # msal adds the openid, profile and offline_access scopes itself
        scopes=[],
        redirect_uri=_redirect_uri(request),
        **account_selection,
    )
    # The flow holds the state, nonce and PKCE verifier checked on the way back
    request.session[ENTRA_ID_FLOW_SESSION_KEY] = flow

    next_url = request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        request.session[ENTRA_ID_NEXT_SESSION_KEY] = next_url
    else:
        request.session.pop(ENTRA_ID_NEXT_SESSION_KEY, None)

    return redirect(flow["auth_uri"])


def _find_user(claims):
    """
    Match the Microsoft account to an Epilepsy12 user by email address. The
    tenant is pinned so these claims can only come from RCPCH's own directory,
    and only addresses on ENTRA_ID_EMAIL_DOMAIN are considered: a guest account
    in the tenant can carry an outside email address in its claims.
    """
    candidate_emails = {
        claims[claim].strip().lower()
        for claim in ("email", "preferred_username", "upn")
        if is_entra_id_email(claims.get(claim))
    }
    if not candidate_emails:
        return None, f"no email address on {settings.ENTRA_ID_EMAIL_DOMAIN}"

    query = Q()
    for email in candidate_emails:
        query |= Q(email__iexact=email)
    matches = list(Epilepsy12User.objects.filter(query)[:2])

    if len(matches) != 1:
        return None, ", ".join(sorted(candidate_emails))
    return matches[0], ", ".join(sorted(candidate_emails))


@require_GET
def entra_id_callback(request):
    """Microsoft redirects back here with an authorisation code."""
    if not settings.ENTRA_ID_LOGIN_ENABLED:
        raise Http404()

    flow = request.session.pop(ENTRA_ID_FLOW_SESSION_KEY, None)
    next_url = request.session.pop(ENTRA_ID_NEXT_SESSION_KEY, None)

    if not flow:
        return _fail(
            request,
            "Your sign in with Microsoft has expired. Please try again.",
            details="No sign in in progress for this session",
        )

    try:
        # Checks the state and nonce, redeems the code (with the PKCE verifier)
        # directly with Microsoft over TLS and validates the ID token's
        # audience, expiry and nonce.
        result = build_entra_id_client().acquire_token_by_auth_code_flow(
            flow, request.GET.dict()
        )
    except ValueError as error:
        return _fail(
            request,
            GENERIC_FAILURE_MESSAGE,
            details=f"Invalid response from Microsoft: {error}",
        )

    if "error" in result:
        return _fail(
            request,
            GENERIC_FAILURE_MESSAGE,
            details=f"{result.get('error')}: {result.get('error_description')}",
        )

    claims = result.get("id_token_claims") or {}

    if claims.get("tid") != settings.ENTRA_ID_TENANT_ID:
        return _fail(
            request,
            GENERIC_FAILURE_MESSAGE,
            details=f"Unexpected tenant {claims.get('tid')}",
        )

    object_id = claims.get("oid")
    if not object_id:
        return _fail(request, GENERIC_FAILURE_MESSAGE, details="No oid claim")

    user, emails = _find_user(claims)

    if user is None:
        return _fail(
            request,
            "There is no Epilepsy12 account for this Microsoft account. Please contact the Epilepsy12 team.",
            details=f"No single Epilepsy12 user matches {emails}",
        )

    if not may_use_entra_id_login(user):
        return _fail(
            request,
            "Sign in with Microsoft is only for superusers and RCPCH Audit Team members. Please sign in with your email and password.",
            user=user,
            details="User is not a superuser or RCPCH Audit Team member",
        )

    if not user.is_active:
        return _fail(
            request,
            "This account is inactive. Please contact the Epilepsy12 team.",
            user=user,
            details="Account is inactive",
        )

    if is_inactive_beyond_deactivation_period(user):
        deactivate_user_for_inactivity(user, request=request)
        return _fail(
            request,
            get_inactivity_deactivation_message(),
            user=user,
            details="Account deactivated due to inactivity",
        )

    device = EntraIDDevice.objects.filter(user=user).first()
    if device is None:
        # First Entra ID sign in: bind this Microsoft account to the user
        device = EntraIDDevice.objects.create(
            user=user,
            name=ENTRA_ID_DEVICE_NAME,
            confirmed=True,
            entra_object_id=object_id,
        )
        logger.info(
            "Bound Entra ID object %s to Epilepsy12 user %s", object_id, user.email
        )
    elif device.entra_object_id != object_id:
        # The email now belongs to a different Microsoft account. Refuse until
        # the binding is reset by deleting the device from the user's logs page.
        return _fail(
            request,
            "This Microsoft account does not match the one previously used for this Epilepsy12 account. Please contact the Epilepsy12 team.",
            user=user,
            details=f"Entra ID object {object_id} does not match bound object {device.entra_object_id}",
        )
    elif not device.confirmed:
        return _fail(
            request,
            "Sign in with Microsoft has been disabled for this account. Please contact the Epilepsy12 team.",
            user=user,
            details="Entra ID device is not confirmed",
        )

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    otp_login(request, device)
    device.set_last_used_timestamp()

    add_post_login_messages(request, user)

    if next_url:
        return redirect(next_url)
    return redirect(get_post_login_url(user))
