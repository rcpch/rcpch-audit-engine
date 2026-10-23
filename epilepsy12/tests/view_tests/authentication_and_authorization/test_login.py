"""
- [ ] user can login with correct credentials
- [ ] user cannot login with wrong credentials
- [ ] failed logins record the reason in the audit trail

- [ ] can create user with correct credentials
- [ ] cannot create user with wrong credentials
"""

# python imports
from http import HTTPStatus
import pytest
import logging

# 3rd party imports
from django.urls import reverse

# E12 imports
from epilepsy12.forms import Epilepsy12UserUpdatePasswordForm
from epilepsy12.models import Epilepsy12User, VisitActivity
from epilepsy12.tests.UserDataClasses import (
    test_user_rcpch_audit_team_data,
)
from epilepsy12.tests.factories import E12UserFactory


@pytest.mark.django_db
def test_pass_validation(
    client,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Testing password reset/creation validation.

    All password validation happens in the form.

    REQUIREMENTS
        Minimum of 10 characters (minimum 16 for RCPCH Audit team)
        Must contain ONE capital
        Must contain ONE number
        Must contain ONE symbol from !@£$%^&*()_-+=|~
        Must NOT be exclusively numbers
        Must NOT be same as your email, name, surname
    """

    rcpch_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    # VALID PASSWORD
    PASSWORD = "Ep!lepsy12_Audit"

    form = Epilepsy12UserUpdatePasswordForm(
        user=rcpch_user,
        data={
            "new_password1": PASSWORD,
            "new_password2": PASSWORD,
        },
    )

    assert form.is_valid()

    INCORRECT_USER_PASSWORD_TOO_SHORT = (
        "Ep!lepsy12"  # 10 digits, 1 capital letter, one digit, one symbol
    )
    INCORRECT_USER_PASSWORD_TOO_SHORT = "Ep!lepsy"
    INCORRECT_USER_PASSWORD_NO_CAPITAL = "ep!lepsy12"
    INCORRECT_USER_PASSWORD_NO_SYMBOL = "Epilepsy12"
    INCORRECT_USER_PASSWORD_NO_NUMBER = "EpilepsyTwelve"
    INCORRECT_USER_PASSWORD_ALL_NUMBERS = "1234567890"
    INCORRECT_USER_PASSWORD_PREDICTABLE = "password"

    incorrect_passwords = [
        INCORRECT_USER_PASSWORD_TOO_SHORT,
        INCORRECT_USER_PASSWORD_TOO_SHORT,
        INCORRECT_USER_PASSWORD_NO_CAPITAL,
        INCORRECT_USER_PASSWORD_NO_SYMBOL,
        INCORRECT_USER_PASSWORD_NO_NUMBER,
        INCORRECT_USER_PASSWORD_ALL_NUMBERS,
        INCORRECT_USER_PASSWORD_PREDICTABLE,
    ]

    for incorrect_password in incorrect_passwords:
        form = Epilepsy12UserUpdatePasswordForm(
            user=rcpch_user,
            data={
                "new_password1": incorrect_password,
                "new_password2": incorrect_password,
            },
        )

    assert form.is_valid() is False


@pytest.mark.django_db
def test_unsuccessful_login_lockout(client, seed_groups_fixture):
    """Testing auto-lockout after 5 unsuccessful login attempts.

    Uses a dedicated user created inside the test transaction so that
    VisitActivity rows from other tests/workers (which share the seeded
    RCPCH_AUDIT_TEAM user under --reuse-db) cannot contaminate the lockout
    counter. Under pytest-xdist, multiple workers can fail logins against
    the shared seeded user concurrently, pre-populating its VisitActivity
    history and triggering lockout at the wrong attempt count.
    """

    # Create a fresh user with a unique email, isolated to this test's
    # transaction. No other test/worker touches this user, so its
    # VisitActivity history only contains rows this test creates.
    rcpch_user = E12UserFactory(
        first_name="LOCKOUT_TEST_USER",
        email="lockout_test_user@nhs.net",
        is_active=True,
    )

    # 5 failed login attempts

    for _ in range(5):

        login_response = client.post(
            reverse('login'),
            data={
                'rcpch_login_view-current_step' : 'auth',
                'auth-username': rcpch_user.email,
                'auth-password' : 'incorrect password',
                'auth-captacha_1': 'PASSED',
            }
        )

    # After 5 failed logins, attempt one more
    login_response = client.post(
            reverse('login'),
            data={
                'rcpch_login_view-current_step' : 'auth',
                'auth-username': rcpch_user.email,
                'auth-password' : 'pw',
                'auth-captacha_1': 'PASSED',
            }
        )

    form = login_response.context['form']
    # this is the item including errors
    assert form.errors['username'][0] == "You have failed to login 5 or more consecutive times. You have been locked out for 10 minutes"


@pytest.mark.django_db
def test_failed_login_records_reason_in_audit_trail(client, seed_groups_fixture):
    """
    Failed logins are audited with the reason, while the message shown to
    the user stays generic. Django scrubs the password before the
    user_login_failed signal fires, so the reason is inferred from the
    account state: an active account with a usable password can only fail
    on the password itself.
    """
    user = E12UserFactory(
        first_name="LOGIN_FAIL_TEST_USER",
        email="login_fail_test_user@nhs.net",
        is_active=True,
    )
    user.set_password("correct-password")
    user.save()

    client.post(
        reverse('login'),
        data={
            'rcpch_login_view-current_step' : 'auth',
            'auth-username': user.email,
            'auth-password' : 'incorrect password',
            'auth-captacha_1': 'PASSED',
        }
    )

    failed_activity = VisitActivity.objects.filter(
        epilepsy12user=user, activity=VisitActivity.UNSUCCESSFUL_LOGIN
    ).first()
    assert failed_activity is not None
    assert failed_activity.details == "Incorrect password"


@pytest.mark.django_db
def test_failed_login_inactive_account_records_reason(client, seed_groups_fixture):
    """
    A correct password on an inactive account fails authentication, and the
    audit trail records the account state as the reason.
    """
    user = E12UserFactory(
        first_name="LOGIN_INACTIVE_TEST_USER",
        email="login_inactive_test_user@nhs.net",
        is_active=False,
    )
    user.set_password("correct-password")
    user.save()

    client.post(
        reverse('login'),
        data={
            'rcpch_login_view-current_step' : 'auth',
            'auth-username': user.email,
            'auth-password' : 'correct-password',
            'auth-captacha_1': 'PASSED',
        }
    )

    failed_activity = VisitActivity.objects.filter(
        epilepsy12user=user, activity=VisitActivity.UNSUCCESSFUL_LOGIN
    ).first()
    assert failed_activity is not None
    assert failed_activity.details == "Account is inactive"


@pytest.mark.django_db
@pytest.mark.skip(reason="https://github.com/rcpch/rcpch-audit-engine/issues/1280")
def test_login_from_direct_link_to_class_based_view(client):
    url = reverse("case_filter_list", kwargs={
        "organisation_id": 1
    })

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("login") + "?next=" + url


@pytest.mark.django_db
def test_login_from_direct_link_to_function_based_view(client):
    url = reverse("selected_organisation_summary", kwargs={
        "organisation_id": 1
    })

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("login") + "?next=" + url