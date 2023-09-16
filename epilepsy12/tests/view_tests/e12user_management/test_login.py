"""
- [ ] user can login with correct credentials
- [ ] user cannot login with wrong credentials
- [ ] user can login if password within 90 days of last update
- [ ] user cannot login if password not within 90 days of last update

- [ ] can create user with correct credentials
- [ ] cannot create user with wrong credentials
"""

# python imports
import pytest
from http import HTTPStatus

# 3rd party imports
from django.urls import reverse

# E12 imports
from epilepsy12.models import Organisation, Epilepsy12User
from epilepsy12.forms import CaptchaAuthenticationForm


@pytest.mark.skip(reason="Unfinished test.")
def test_login_with_correct_credentials(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,
    URL,
):
    """
    Simulating different E12 users trying to sign up with correct credentials
    """

    # Constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    E12USER = "bill.bailey@nhs.net"
    CORRECT_USER_PASSWORD = (
        "Ep!lepsy12"  # 10 digits, 1 capital letter, one digit, one symbol
    )
    CORRECT_RCPCH_USER_PASSWORD = (
        "Ep!lepsy12_Audit"  # 16 digits, 1 capital letter, one digit, one symbol
    )
    INCORRECT_USER_PASSWORD_TOO_SHORT = (
        "Ep!lepsy12"  # 10 digits, 1 capital letter, one digit, one symbol
    )
    INCORRECT_USER_PASSWORD_TOO_SHORT = "Ep!lepsy"
    INCORRECT_USER_PASSWORD_NO_CAPITAL = "ep!lepsy12"
    INCORRECT_USER_PASSWORD_NO_SYMBOL = "Epilepsy12"
    INCORRECT_USER_PASSWORD_NO_NUMBER = "EpilepsyTwelve"
    INCORRECT_USER_PASSWORD_ALL_NUMBERS = "1234567890"
    INCORRECT_USER_PASSWORD_PREDICTABLE = "password"

    passwords = [
        INCORRECT_USER_PASSWORD_TOO_SHORT,
        INCORRECT_USER_PASSWORD_TOO_SHORT,
        INCORRECT_USER_PASSWORD_NO_CAPITAL,
        INCORRECT_USER_PASSWORD_NO_SYMBOL,
        INCORRECT_USER_PASSWORD_NO_NUMBER,
        INCORRECT_USER_PASSWORD_ALL_NUMBERS,
        INCORRECT_USER_PASSWORD_PREDICTABLE,
    ]

    extra_fields = {"organisation_employer": TEST_USER_ORGANISATION}

    user = Epilepsy12User.objects.create_user(
        email=E12USER,
        password=CORRECT_USER_PASSWORD,
        first_name="Bill",
        surname="Bailey",
        role=1,
        **extra_fields,
    )

    data = {"email": E12USER, "password": CORRECT_USER_PASSWORD}

    login_response = client.post(reverse("login"), data=data)

    assert (
        login_response.status_code == HTTPStatus.OK
    ), f"{user.first_name} (from {user.organisation_employer}) logged in. Expected 200 response status code, received {login_response.status_code}"
