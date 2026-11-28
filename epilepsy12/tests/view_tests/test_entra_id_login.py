"""
Tests for signing in with Microsoft Entra ID, and for the
ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF setting that makes it compulsory for
superusers and the RCPCH Audit Team.

Microsoft is never contacted: the msal client is replaced with a fake that
returns the ID token claims we choose.
"""

import os
import re
import subprocess
import sys
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_CLINICIAN,
    RCPCH_AUDIT_TEAM,
)
from epilepsy12.forms_folder.epilepsy12_user_form import CaptchaAuthenticationForm
from epilepsy12.general_functions import entra_id as entra_id_module
from epilepsy12.general_functions.entra_id import (
    build_entra_id_client,
    get_managed_identity_assertion,
    is_entra_id_email,
    may_use_entra_id_login,
    must_use_entra_id_login,
)
from epilepsy12.models import EntraIDDevice, Epilepsy12User, VisitActivity
from epilepsy12.views.entra_id_views import (
    ENTRA_ID_FLOW_SESSION_KEY,
    ENTRA_ID_NEXT_SESSION_KEY,
)

TENANT_ID = "11111111-2222-3333-4444-555555555555"
OBJECT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

ENTRA_CONFIGURED = dict(
    ENTRA_ID_TENANT_ID=TENANT_ID,
    ENTRA_ID_CLIENT_ID="client-id",
    ENTRA_ID_CLIENT_SECRET="client-secret",
    ENTRA_ID_EMAIL_DOMAIN="rcpch.ac.uk",
    ENTRA_ID_LOGIN_ENABLED=True,
)
ENTRA_REQUIRED = dict(ENTRA_CONFIGURED, ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF=True)
ENTRA_OPTIONAL = dict(ENTRA_CONFIGURED, ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF=False)


class FakeEntraClient:
    """Stands in for msal.ConfidentialClientApplication."""

    def __init__(self, result=None, raises=None):
        self.result = result
        self.raises = raises
        self.redeemed_with = None

    def initiate_auth_code_flow(self, scopes, redirect_uri, **kwargs):
        self.redirect_uri = redirect_uri
        self.account_selection = kwargs
        return {
            "auth_uri": "https://login.microsoftonline.com/authorize?state=abc",
            "state": "abc",
        }

    def acquire_token_by_auth_code_flow(self, flow, auth_response):
        self.redeemed_with = (flow, auth_response)
        if self.raises:
            raise self.raises
        return self.result


def claims_for(preferred_username, tid=TENANT_ID, oid=OBJECT_ID, **extra):
    claims = {
        "tid": tid,
        "oid": oid,
        "preferred_username": preferred_username,
        **extra,
    }
    return {"id_token_claims": claims}


def complete_entra_sign_in(client, fake_client, next_url=None):
    session = client.session
    session[ENTRA_ID_FLOW_SESSION_KEY] = {"state": "abc"}
    if next_url:
        session[ENTRA_ID_NEXT_SESSION_KEY] = next_url
    session.save()

    with patch(
        "epilepsy12.views.entra_id_views.build_entra_id_client",
        return_value=fake_client,
    ):
        return client.get(
            reverse("entra_id_callback"), {"code": "the-code", "state": "abc"}
        )


def saved(user):
    # The factory sets a password without saving it, which would invalidate a
    # session started with client.force_login(user)
    user.refresh_from_db()
    return user


@pytest.fixture
def superuser(e12_user_factory):
    return saved(
        e12_user_factory(
            role=RCPCH_AUDIT_TEAM, is_superuser=True, email="super@rcpch.ac.uk"
        )
    )


@pytest.fixture
def audit_team_member(e12_user_factory):
    return saved(
        e12_user_factory(role=RCPCH_AUDIT_TEAM, email="audit.team@rcpch.ac.uk")
    )


@pytest.fixture
def clinician(e12_user_factory):
    return saved(
        e12_user_factory(
            role=AUDIT_CENTRE_CLINICIAN,
            email="first.last+lead_clinician@rcpch.ac.uk",
        )
    )


# Who the setting covers


@override_settings(ENTRA_ID_EMAIL_DOMAIN="rcpch.ac.uk")
@pytest.mark.parametrize(
    "email,expected",
    [
        ("someone@rcpch.ac.uk", True),
        ("  Someone@RCPCH.ac.uk ", True),
        ("first.last+lead_clinician@rcpch.ac.uk", True),
        ("someone@nhs.net", False),
        ("someone@notrcpch.ac.uk", False),
        ("someone@rcpch.ac.uk.evil.com", False),
        ("@rcpch.ac.uk", False),
        ("rcpch.ac.uk", False),
        ("", False),
        (None, False),
    ],
)
def test_is_entra_id_email(email, expected):
    assert is_entra_id_email(email) is expected


@override_settings(ENTRA_ID_EMAIL_DOMAIN="")
def test_no_email_is_entra_id_email_without_a_domain():
    assert is_entra_id_email("someone@rcpch.ac.uk") is False


@pytest.mark.django_db
def test_superusers_and_audit_team_may_use_entra_id(
    superuser, audit_team_member, clinician
):
    assert may_use_entra_id_login(superuser)
    assert may_use_entra_id_login(audit_team_member)
    assert not may_use_entra_id_login(clinician)


@pytest.mark.django_db
def test_superuser_with_clinician_role_may_use_entra_id(e12_user_factory):
    user = e12_user_factory(role=AUDIT_CENTRE_CLINICIAN, is_superuser=True)

    assert may_use_entra_id_login(user)


@pytest.mark.django_db
def test_entra_id_only_compulsory_when_setting_is_on(superuser, clinician):
    with override_settings(ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF=False):
        assert not must_use_entra_id_login(superuser)

    with override_settings(ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF=True):
        assert must_use_entra_id_login(superuser)
        assert not must_use_entra_id_login(clinician)


# Password login (CaptchaAuthenticationForm.confirm_login_allowed)


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
@pytest.mark.parametrize("user_fixture", ["superuser", "audit_team_member"])
def test_password_login_refused_for_rcpch_staff_when_required(request, user_fixture):
    user = request.getfixturevalue(user_fixture)
    user.set_password("A-Valid-Password-1!")
    user.save()
    TOTPDevice.objects.create(user=user, name="default")
    password_hash = user.password

    form = CaptchaAuthenticationForm(request=None)
    with pytest.raises(ValidationError) as excinfo:
        form.confirm_login_allowed(user)

    # The same error as a wrong password, so a correct password is not revealed
    assert excinfo.value.code == "invalid_login"

    refused = VisitActivity.objects.get(
        epilepsy12user=user, activity=VisitActivity.UNSUCCESSFUL_LOGIN
    )
    assert "Entra ID" in refused.details

    # Credentials are left in place so the setting can be switched off again
    user.refresh_from_db()
    assert user.password == password_hash
    assert user.has_usable_password()
    assert TOTPDevice.objects.filter(user=user, name="default").exists()


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_password_login_allowed_for_rcpch_staff_when_not_required(superuser):
    form = CaptchaAuthenticationForm(request=None)

    form.confirm_login_allowed(superuser)  # does not raise


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_password_login_allowed_for_clinicians_when_required(clinician):
    form = CaptchaAuthenticationForm(request=None)

    form.confirm_login_allowed(clinician)  # does not raise


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_password_login_view_refuses_rcpch_staff_when_required(client, superuser):
    superuser.set_password("A-Valid-Password-1!")
    superuser.save()

    with patch("captcha.conf.settings.CAPTCHA_TEST_MODE", True):
        response = client.post(
            reverse("two_factor:login"),
            {
                "rcpch_login_view-current_step": "auth",
                "auth-username": superuser.email,
                "auth-password": "A-Valid-Password-1!",
                "auth-captcha_0": "x",
                "auth-captcha_1": "PASSED",
            },
        )

    assert response.status_code == 200
    form = response.context["form"]
    # The normal "incorrect email or password" error
    assert form.non_field_errors().as_data()[0].code == "invalid_login"
    assert "_auth_user_id" not in client.session

    # Sign in with Microsoft is shown because the email is on the domain
    assert response.context["entra_id_login_hint"] == superuser.email


def post_password_login(client, email, password):
    with patch("captcha.conf.settings.CAPTCHA_TEST_MODE", True):
        return client.post(
            reverse("two_factor:login"),
            {
                "rcpch_login_view-current_step": "auth",
                "auth-username": email,
                "auth-password": password,
                "auth-captcha_0": "x",
                "auth-captcha_1": "PASSED",
            },
        )


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_refused_staff_password_looks_the_same_as_a_wrong_password(client, superuser):
    superuser.set_password("A-Valid-Password-1!")
    superuser.save()

    correct = post_password_login(client, superuser.email, "A-Valid-Password-1!")
    wrong = post_password_login(client, superuser.email, "Not-The-Password-1!")

    assert (
        correct.context["form"].non_field_errors()
        == wrong.context["form"].non_field_errors()
    )
    assert (
        correct.context["entra_id_login_hint"] == wrong.context["entra_id_login_hint"]
    )


# Login page


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_login_page_hides_sign_in_with_microsoft_until_domain_email_typed(client):
    response = client.get(reverse("two_factor:login"))

    # Present for the JavaScript to reveal, but hidden
    assert b'data-email-domain="rcpch.ac.uk"' in response.content
    assert response.context["entra_id_login_hint"] == ""
    assert re.search(rb'<div id="entra_id_login"[^>]*\shidden\s*>', response.content)


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_login_page_shows_sign_in_with_microsoft_for_domain_email_without_js(
    client,
):
    response = post_password_login(client, "Nobody@RCPCH.ac.uk", "x")

    assert response.context["entra_id_login_hint"] == "nobody@rcpch.ac.uk"
    assert not re.search(
        rb'<div id="entra_id_login"[^>]*\shidden\s*>', response.content
    )
    assert b"login_hint=nobody%40rcpch.ac.uk" in response.content


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_login_page_keeps_sign_in_with_microsoft_hidden_for_other_emails(client):
    response = post_password_login(client, "clinician@nhs.net", "x")

    assert response.context["entra_id_login_hint"] == ""


@pytest.mark.django_db
@override_settings(ENTRA_ID_LOGIN_ENABLED=False)
def test_login_page_hides_sign_in_with_microsoft_when_not_configured(client):
    response = client.get(reverse("two_factor:login"))

    assert b"Sign in with Microsoft" not in response.content


@pytest.mark.django_db
@override_settings(ENTRA_ID_LOGIN_ENABLED=False)
def test_entra_id_routes_404_when_not_configured(client):
    assert client.get(reverse("entra_id_login")).status_code == 404
    assert client.get(reverse("entra_id_callback")).status_code == 404


# Starting the sign in


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_entra_id_login_redirects_to_microsoft_and_keeps_safe_next(client):
    fake = FakeEntraClient()
    with patch(
        "epilepsy12.views.entra_id_views.build_entra_id_client", return_value=fake
    ):
        response = client.get(reverse("entra_id_login"), {"next": "/admin/"})

    assert response.status_code == 302
    assert response.url.startswith("https://login.microsoftonline.com/")
    assert fake.redirect_uri.endswith(reverse("entra_id_callback"))
    assert client.session[ENTRA_ID_FLOW_SESSION_KEY]["state"] == "abc"
    assert client.session[ENTRA_ID_NEXT_SESSION_KEY] == "/admin/"
    assert fake.account_selection == {"prompt": "select_account"}


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_entra_id_login_passes_domain_email_to_microsoft(client):
    fake = FakeEntraClient()
    with patch(
        "epilepsy12.views.entra_id_views.build_entra_id_client", return_value=fake
    ):
        client.get(reverse("entra_id_login"), {"login_hint": "Super@rcpch.ac.uk"})

    assert fake.account_selection == {"login_hint": "super@rcpch.ac.uk"}


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_entra_id_login_ignores_login_hint_off_domain(client):
    fake = FakeEntraClient()
    with patch(
        "epilepsy12.views.entra_id_views.build_entra_id_client", return_value=fake
    ):
        client.get(reverse("entra_id_login"), {"login_hint": "someone@nhs.net"})

    assert fake.account_selection == {"prompt": "select_account"}


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_entra_id_login_ignores_external_next(client):
    with patch(
        "epilepsy12.views.entra_id_views.build_entra_id_client",
        return_value=FakeEntraClient(),
    ):
        client.get(reverse("entra_id_login"), {"next": "https://evil.example.com/"})

    assert ENTRA_ID_NEXT_SESSION_KEY not in client.session


# Completing the sign in


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
@pytest.mark.parametrize("user_fixture", ["superuser", "audit_team_member"])
def test_entra_id_sign_in_logs_in_and_verifies_rcpch_staff(
    client, request, user_fixture
):
    user = request.getfixturevalue(user_fixture)
    fake = FakeEntraClient(result=claims_for(user.email.upper()))

    response = complete_entra_sign_in(client, fake, next_url="/admin/")

    assert response.status_code == 302
    assert response.url == "/admin/"
    assert fake.redeemed_with == (
        {"state": "abc"},
        {"code": "the-code", "state": "abc"},
    )
    assert int(client.session["_auth_user_id"]) == user.pk
    assert ENTRA_ID_FLOW_SESSION_KEY not in client.session

    device = EntraIDDevice.objects.get(user=user)
    assert device.entra_object_id == OBJECT_ID
    assert device.last_used_at is not None
    assert client.session[DEVICE_ID_SESSION_KEY] == device.persistent_id

    assert VisitActivity.objects.filter(
        epilepsy12user=user, activity=VisitActivity.SUCCESSFUL_LOGIN
    ).exists()

    # The session counts as 2FA verified
    response = client.get(reverse("index"))
    assert response.status_code == 200
    assert response.wsgi_request.user.is_verified()
    assert int(client.session["_auth_user_id"]) == user.pk


@pytest.mark.django_db
@override_settings(**ENTRA_OPTIONAL)
def test_entra_id_sign_in_works_when_not_required(client, superuser):
    response = complete_entra_sign_in(
        client, FakeEntraClient(claims_for(superuser.email))
    )

    assert response.status_code == 302
    assert int(client.session["_auth_user_id"]) == superuser.pk


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_reuses_bound_device(client, superuser):
    EntraIDDevice.objects.create(
        user=superuser, name="Entra ID", entra_object_id=OBJECT_ID
    )

    complete_entra_sign_in(client, FakeEntraClient(claims_for(superuser.email)))

    assert int(client.session["_auth_user_id"]) == superuser.pk
    assert EntraIDDevice.objects.filter(user=superuser).count() == 1


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_ignores_email_claims_off_domain(client, e12_user_factory):
    """
    A guest account in the tenant can carry an outside email address in its
    claims. Only addresses on ENTRA_ID_EMAIL_DOMAIN are matched to users.
    """
    outside_superuser = saved(
        e12_user_factory(
            role=RCPCH_AUDIT_TEAM, is_superuser=True, email="developer@example.com"
        )
    )

    response = complete_entra_sign_in(
        client,
        FakeEntraClient(
            claims_for(
                "developer_example.com#EXT#@rcpch.onmicrosoft.com",
                email="developer@example.com",
            )
        ),
    )

    assert_refused(client, response)
    assert not EntraIDDevice.objects.filter(user=outside_superuser).exists()


def assert_refused(client, response, user=None, details_contains=None):
    assert response.status_code == 302
    assert response.url == reverse("two_factor:login")
    assert "_auth_user_id" not in client.session
    if user is not None:
        failure = VisitActivity.objects.get(
            epilepsy12user=user, activity=VisitActivity.UNSUCCESSFUL_LOGIN
        )
        assert failure.details.startswith("Microsoft Entra ID sign in failed: ")
        if details_contains:
            assert details_contains in failure.details


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_refused_for_clinicians(client, clinician):
    response = complete_entra_sign_in(
        client, FakeEntraClient(claims_for(clinician.email))
    )

    assert_refused(client, response, clinician, "not a superuser")
    assert not EntraIDDevice.objects.filter(user=clinician).exists()


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_refused_for_other_tenant(client, superuser):
    response = complete_entra_sign_in(
        client, FakeEntraClient(claims_for(superuser.email, tid="another-tenant"))
    )

    assert_refused(client, response)
    assert not EntraIDDevice.objects.filter(user=superuser).exists()


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_refused_for_unknown_email(client, superuser):
    response = complete_entra_sign_in(
        client, FakeEntraClient(claims_for("nobody@rcpch.ac.uk"))
    )

    assert_refused(client, response)


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_refused_for_inactive_user(client, superuser):
    superuser.is_active = False
    superuser.save()

    response = complete_entra_sign_in(
        client, FakeEntraClient(claims_for(superuser.email))
    )

    assert_refused(client, response, superuser, "inactive")


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_refused_when_microsoft_account_changes(client, superuser):
    EntraIDDevice.objects.create(
        user=superuser, name="Entra ID", entra_object_id="a-different-object-id"
    )

    response = complete_entra_sign_in(
        client, FakeEntraClient(claims_for(superuser.email))
    )

    assert_refused(client, response, superuser, "does not match")


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_refused_when_microsoft_returns_error(client, superuser):
    response = complete_entra_sign_in(
        client,
        FakeEntraClient(
            {"error": "access_denied", "error_description": "User cancelled"}
        ),
    )

    assert_refused(client, response)


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_refused_when_state_does_not_match(client, superuser):
    response = complete_entra_sign_in(
        client, FakeEntraClient(raises=ValueError("state mismatch"))
    )

    assert_refused(client, response)


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_callback_refused_without_sign_in_in_progress(client, superuser):
    fake = FakeEntraClient(claims_for(superuser.email))
    with patch(
        "epilepsy12.views.entra_id_views.build_entra_id_client", return_value=fake
    ):
        response = client.get(reverse("entra_id_callback"), {"code": "x"})

    assert_refused(client, response)
    assert fake.redeemed_with is None


# How the app authenticates to Entra ID (build_entra_id_client)


@pytest.fixture
def fresh_managed_identity_credential():
    """Clear the cached credential so each test builds its own."""
    entra_id_module._managed_identity_credential = None
    yield
    entra_id_module._managed_identity_credential = None


@override_settings(
    **dict(
        ENTRA_CONFIGURED,
        ENTRA_ID_CLIENT_SECRET="client-secret",
        ENTRA_ID_USE_MANAGED_IDENTITY=False,
    )
)
def test_entra_id_client_uses_client_secret():
    with patch("msal.ConfidentialClientApplication") as client_class:
        build_entra_id_client()

    kwargs = client_class.call_args.kwargs
    assert kwargs["client_id"] == "client-id"
    assert kwargs["client_credential"] == "client-secret"
    assert kwargs["authority"] == f"https://login.microsoftonline.com/{TENANT_ID}"


@override_settings(
    **dict(
        ENTRA_CONFIGURED,
        ENTRA_ID_CLIENT_SECRET="",
        ENTRA_ID_USE_MANAGED_IDENTITY=True,
        ENTRA_ID_MANAGED_IDENTITY_CLIENT_ID="managed-identity-client-id",
    )
)
def test_entra_id_client_uses_managed_identity_as_client_assertion(
    fresh_managed_identity_credential,
):
    with patch("msal.ConfidentialClientApplication") as client_class, patch(
        "azure.identity.ManagedIdentityCredential"
    ) as credential_class:
        credential_class.return_value.get_token.return_value.token = "mi-token"

        build_entra_id_client()
        client_credential = client_class.call_args.kwargs["client_credential"]

        # msal calls the assertion each time it needs one, so it stays current
        assert set(client_credential) == {"client_assertion"}
        assert client_credential["client_assertion"]() == "mi-token"
        assert client_credential["client_assertion"]() == "mi-token"

    credential_class.assert_called_once_with(client_id="managed-identity-client-id")
    credential_class.return_value.get_token.assert_called_with(
        "api://AzureADTokenExchange/.default"
    )


@override_settings(
    **dict(
        ENTRA_CONFIGURED,
        ENTRA_ID_CLIENT_SECRET="",
        ENTRA_ID_USE_MANAGED_IDENTITY=True,
        ENTRA_ID_MANAGED_IDENTITY_CLIENT_ID="",
    )
)
def test_entra_id_client_uses_system_assigned_identity_without_a_client_id(
    fresh_managed_identity_credential,
):
    with patch("azure.identity.ManagedIdentityCredential") as credential_class:
        credential_class.return_value.get_token.return_value.token = "mi-token"
        get_managed_identity_assertion()

    credential_class.assert_called_once_with(client_id=None)


def _import_settings_with(env_overrides):
    """Import the settings module in a fresh interpreter with these env vars."""
    env = {
        **os.environ,
        "ENTRA_ID_TENANT_ID": TENANT_ID,
        "ENTRA_ID_CLIENT_ID": "client-id",
        "ENTRA_ID_EMAIL_DOMAIN": "rcpch.ac.uk",
        "ENTRA_ID_CLIENT_SECRET": "",
        "ENTRA_ID_USE_MANAGED_IDENTITY": "False",
        "ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF": "False",
        **env_overrides,
    }
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "import importlib, sys; sys.path.insert(0, '.'); "
            "s = importlib.import_module('rcpch-audit-engine.settings'); "
            "print('ENABLED', s.ENTRA_ID_LOGIN_ENABLED)",
        ],
        cwd=settings.BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
    )


def test_settings_refuse_both_client_secret_and_managed_identity():
    result = _import_settings_with(
        {"ENTRA_ID_CLIENT_SECRET": "secret", "ENTRA_ID_USE_MANAGED_IDENTITY": "True"}
    )

    assert result.returncode != 0
    assert "Set only one of ENTRA_ID_CLIENT_SECRET" in result.stderr


@pytest.mark.parametrize(
    "credential_env",
    [
        {"ENTRA_ID_CLIENT_SECRET": "secret"},
        {"ENTRA_ID_USE_MANAGED_IDENTITY": "True"},
    ],
)
def test_settings_enable_entra_id_with_either_credential(credential_env):
    result = _import_settings_with(credential_env)

    assert result.returncode == 0, result.stderr
    assert "ENABLED True" in result.stdout


def test_settings_disable_entra_id_without_a_credential():
    result = _import_settings_with({})

    assert result.returncode == 0, result.stderr
    assert "ENABLED False" in result.stdout


# Review fixes: admin alerts, one binding per user, email confirmation


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_anonymous_callback_failures_do_not_email_admins(client):
    """
    Anyone can request the callback, so failures before Microsoft has returned
    a valid ID token are logged as warnings, not emailed to the admins.
    """
    with patch("epilepsy12.views.entra_id_views.logger") as logger:
        # No sign in in progress
        client.get(reverse("entra_id_callback"), {"code": "x"})
        # State mismatch
        complete_entra_sign_in(client, FakeEntraClient(raises=ValueError("state")))
        # User cancelled, or a made-up code
        complete_entra_sign_in(
            client,
            FakeEntraClient({"error": "access_denied", "error_description": "no"}),
        )
        complete_entra_sign_in(
            client,
            FakeEntraClient({"error": "invalid_grant", "error_description": "no"}),
        )

    assert logger.warning.call_count == 4
    logger.error.assert_not_called()


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_configuration_errors_email_admins(client):
    """An expired secret or wrong federated credential needs fixing."""
    with patch("epilepsy12.views.entra_id_views.logger") as logger:
        complete_entra_sign_in(
            client,
            FakeEntraClient(
                {"error": "invalid_client", "error_description": "AADSTS7000215"}
            ),
        )

    logger.error.assert_called_once()


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_configuration_error_in_the_callback_itself_does_not_email_admins(client):
    """
    Without a code, msal returns the error from the callback's query string
    without contacting Microsoft, so anyone who has started a sign in can
    supply it. Only an error from redeeming a code is a real configuration
    error.
    """
    session = client.session
    session[ENTRA_ID_FLOW_SESSION_KEY] = {"state": "abc"}
    session.save()
    forged = {
        "state": "abc",
        "error": "invalid_client",
        "error_description": "anything the caller likes",
    }

    with (
        patch(
            "epilepsy12.views.entra_id_views.build_entra_id_client",
            return_value=FakeEntraClient(
                {k: v for k, v in forged.items() if k != "state"}
            ),
        ),
        patch("epilepsy12.views.entra_id_views.logger") as logger,
    ):
        response = client.get(reverse("entra_id_callback"), forged)

    assert_refused(client, response)
    logger.error.assert_not_called()
    logger.warning.assert_called_once()


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_failures_for_a_validated_microsoft_account_email_admins(client, clinician):
    with patch("epilepsy12.views.entra_id_views.logger") as logger:
        complete_entra_sign_in(client, FakeEntraClient(claims_for(clinician.email)))

    logger.error.assert_called_once()
    logger.warning.assert_not_called()


@pytest.mark.django_db
def test_a_user_can_have_only_one_entra_id_device(superuser):
    EntraIDDevice.objects.create(
        user=superuser, name="Entra ID", entra_object_id=OBJECT_ID
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        EntraIDDevice.objects.create(
            user=superuser, name="Entra ID", entra_object_id="another-object-id"
        )


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_entra_id_sign_in_confirms_email_of_passwordless_user(
    client, audit_team_member
):
    """
    New Audit Team members who only sign in with Microsoft never set a
    password, so email_confirmed would otherwise stay False and deny them
    access to patient records.
    """
    Epilepsy12User.objects.filter(pk=audit_team_member.pk).update(
        email_confirmed=False, password="!unusable"
    )
    audit_team_member.refresh_from_db()
    assert not audit_team_member.has_usable_password()

    complete_entra_sign_in(client, FakeEntraClient(claims_for(audit_team_member.email)))

    assert int(client.session["_auth_user_id"]) == audit_team_member.pk
    audit_team_member.refresh_from_db()
    assert audit_team_member.email_confirmed
    assert not audit_team_member.has_usable_password()


@pytest.mark.django_db
@override_settings(**ENTRA_REQUIRED)
def test_refused_entra_id_sign_in_does_not_confirm_email(client, clinician):
    Epilepsy12User.objects.filter(pk=clinician.pk).update(email_confirmed=False)

    complete_entra_sign_in(client, FakeEntraClient(claims_for(clinician.email)))

    clinician.refresh_from_db()
    assert not clinician.email_confirmed
