"""
Helpers for signing in with Microsoft Entra ID (OAuth 2.0 / OpenID Connect).

Superusers and RCPCH Audit Team members may sign in with their RCPCH Microsoft
account. When settings.ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF is True they
must: the email, password and one-time code login is refused for them.
"""

from django.conf import settings

from epilepsy12.constants.user_types import RCPCH_AUDIT_TEAM

ENTRA_ID_LOGIN_REQUIRED_MESSAGE = (
    "Superusers and RCPCH Audit Team members must sign in with Microsoft."
)


def may_use_entra_id_login(user) -> bool:
    """Superusers and RCPCH Audit Team members may sign in with Entra ID."""
    return bool(user.is_superuser or user.role == RCPCH_AUDIT_TEAM)


def must_use_entra_id_login(user) -> bool:
    """
    True if this user may only sign in with Entra ID. Read at call time so the
    setting can be switched off again without touching any user's credentials.
    """
    return bool(
        settings.ENTRA_ID_LOGIN_REQUIRED_FOR_RCPCH_STAFF
        and may_use_entra_id_login(user)
    )


def build_entra_id_client():
    # Imported here so msal is only loaded when Entra ID sign in is used
    import msal

    return msal.ConfidentialClientApplication(
        client_id=settings.ENTRA_ID_CLIENT_ID,
        client_credential=settings.ENTRA_ID_CLIENT_SECRET,
        # Single tenant: only RCPCH accounts can sign in
        authority=f"https://login.microsoftonline.com/{settings.ENTRA_ID_TENANT_ID}",
    )
