"""
Tests for the password reset flow audit trail.

- [ ] a failed password reset attempt (password rejected by validation) is
      recorded in the audit trail with the validation errors, and does not
      change the password
- [ ] a successful password reset is recorded in the audit trail and changes
      the password
"""

# third party imports
import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# E12 imports
from epilepsy12.models import VisitActivity
from epilepsy12.tests.factories import E12UserFactory

ORIGINAL_PASSWORD = "original-password"


def create_user_with_password(first_name, email):
    """
    E12UserFactory does not persist the password its post-generation hook
    sets (skip_postgeneration_save), so set and save one explicitly.
    """
    user = E12UserFactory(first_name=first_name, email=email, is_active=True)
    user.set_password(ORIGINAL_PASSWORD)
    user.save()
    return user


def reset_urls(user):
    """
    Return (link_url, set_password_url) for a freshly generated reset token.

    Clicking link_url stores the token in the session and redirects to the
    token-less set-password URL (Django 5.2 PasswordResetConfirmView
    behaviour), which is where the new password is submitted.
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"/reset/{uidb64}/{token}/", f"/reset/{uidb64}/set-password/"


@pytest.mark.django_db
def test_failed_password_reset_attempt_is_audited(client, seed_groups_fixture):
    """
    A password reset submission that fails validation must leave an audit
    trail: the response is a 200 re-render of the form, so without a
    VisitActivity entry the failure is indistinguishable from simply
    viewing the form page in the request logs.
    """
    user = create_user_with_password(
        first_name="RESET_FAIL_TEST_USER",
        email="reset_fail_test_user@nhs.net",
    )

    link_url, set_password_url = reset_urls(user)

    # Phase 1: clicking the emailed link redirects to the set-password form
    response = client.get(link_url, follow=True)
    assert response.status_code == 200

    # Submit a password that fails validation
    response = client.post(
        set_password_url,
        data={"new_password1": "short", "new_password2": "short"},
    )
    assert response.status_code == 200  # form re-rendered with errors

    failed_activity = VisitActivity.objects.filter(
        epilepsy12user=user, activity=VisitActivity.PASSWORD_RESET_FAILED
    ).first()
    assert failed_activity is not None
    assert "too short" in failed_activity.details

    # The password must not have changed...
    user.refresh_from_db()
    assert user.check_password(ORIGINAL_PASSWORD)

    # ...and no successful reset may have been recorded
    assert not VisitActivity.objects.filter(
        epilepsy12user=user, activity=VisitActivity.PASSWORD_RESET
    ).exists()


@pytest.mark.django_db
def test_successful_password_reset_is_audited(client, seed_groups_fixture):
    """
    For contrast with the failed attempt: a valid submission changes the
    password and records the PASSWORD_RESET activity.
    """
    user = create_user_with_password(
        first_name="RESET_SUCCESS_TEST_USER",
        email="reset_success_test_user@nhs.net",
    )

    link_url, set_password_url = reset_urls(user)

    response = client.get(link_url, follow=True)
    assert response.status_code == 200

    new_password = "Correct-Horse!9"
    response = client.post(
        set_password_url,
        data={"new_password1": new_password, "new_password2": new_password},
        follow=True,
    )
    assert response.status_code == 200  # followed redirect to /reset/done/

    user.refresh_from_db()
    assert user.check_password(new_password)
    assert VisitActivity.objects.filter(
        epilepsy12user=user, activity=VisitActivity.PASSWORD_RESET
    ).exists()
