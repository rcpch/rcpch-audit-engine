"""
Tests for deactivation of user accounts after a prolonged period of
inactivity (settings.ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS).

The check runs when credentials are validated at login, in
CaptchaAuthenticationForm.confirm_login_allowed (the two-factor wizard's
auth step). Reactivation by an administrator (a lead clinician reactivating
via the user edit view) restarts the clock, so a reactivated user is not
immediately re-deactivated at their next login attempt.
"""

from datetime import timedelta
from http import HTTPStatus

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_LEAD_CLINICIAN,
)
from epilepsy12.forms_folder.epilepsy12_user_form import CaptchaAuthenticationForm
from epilepsy12.general_functions.inactivity_deactivation import (
    get_inactivity_deactivation_message,
    is_inactive_beyond_deactivation_period,
)
from epilepsy12.models import Epilepsy12User, VisitActivity
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_lead_clinician_data,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)

INACTIVITY_PERIOD_DAYS = 730


# is_inactive_beyond_deactivation_period


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_recently_active_user_is_not_flagged_for_deactivation(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=timezone.now() - timedelta(days=30),
    )

    assert is_inactive_beyond_deactivation_period(user) is False


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_user_inactive_beyond_period_is_flagged_for_deactivation(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=timezone.now() - timedelta(days=731),
    )

    assert is_inactive_beyond_deactivation_period(user) is True


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_never_logged_in_user_flagged_if_account_created_beyond_period(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=None,
        date_joined=timezone.now() - timedelta(days=1000),
    )

    assert is_inactive_beyond_deactivation_period(user) is True


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_never_logged_in_user_not_flagged_if_recently_joined(e12_user_factory):
    user = e12_user_factory(role=AUDIT_CENTRE_CLINICIAN, last_login=None)

    assert is_inactive_beyond_deactivation_period(user) is False


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_superuser_never_flagged_for_deactivation(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        is_superuser=True,
        last_login=timezone.now() - timedelta(days=2000),
    )

    assert is_inactive_beyond_deactivation_period(user) is False


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=0)
def test_deactivation_check_disabled_when_period_is_zero(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=timezone.now() - timedelta(days=2000),
    )

    assert is_inactive_beyond_deactivation_period(user) is False


# CaptchaAuthenticationForm.confirm_login_allowed (production login path)


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_confirm_login_allowed_deactivates_user_inactive_beyond_period(
    e12_user_factory,
):
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=timezone.now() - timedelta(days=800),
    )

    form = CaptchaAuthenticationForm(request=None)

    with pytest.raises(ValidationError) as excinfo:
        form.confirm_login_allowed(user)

    assert "deactivated" in str(excinfo.value)

    user.refresh_from_db()
    assert user.is_active is False

    # An audit log entry records the deactivation and its reason
    deactivation_activity = VisitActivity.objects.filter(
        epilepsy12user=user, activity=VisitActivity.ACCOUNT_DEACTIVATED_INACTIVITY
    ).get()
    assert "deactivated due to inactivity" in deactivation_activity.details
    assert VisitActivity.CHANGED_ADMIN_FLAG in VisitActivity.objects.filter(
        epilepsy12user=user
    ).values_list("activity", flat=True)


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_confirm_login_allowed_allows_recently_active_user(e12_user_factory):
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=timezone.now() - timedelta(days=30),
    )

    form = CaptchaAuthenticationForm(request=None)
    form.confirm_login_allowed(user)  # should not raise

    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
@override_settings(SITE_CONTACT_EMAIL="epilepsy12@rcpch.ac.uk")
def test_deactivation_message_directs_user_to_the_epilepsy12_team():
    """
    The login page message is the only notification the user receives, so it
    must tell them how to get their account reactivated.
    """
    message = get_inactivity_deactivation_message()

    assert "deactivated due to inactivity" in message
    assert "epilepsy12@rcpch.ac.uk" in message


# Reactivation by a lead clinician


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_lead_clinician_can_reactivate_user_deactivated_for_inactivity(
    GOSH,
    client,
):
    """
    A user deactivated for inactivity, then reactivated by their lead
    clinician, must not be immediately re-deactivated at their next login
    attempt.
    """
    lead_clinician = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )
    assert lead_clinician.organisation_employer == GOSH

    user = Epilepsy12User.objects.create(
        email="inactive-user@test.com",
        first_name="Inactive",
        surname="User",
        role=AUDIT_CENTRE_CLINICIAN,
        is_active=True,
        email_confirmed=True,
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
        last_login=timezone.now() - timedelta(days=800),
    )
    user.set_organisation_employer(organisation_employer=GOSH, is_primary=True)

    # The user's login attempt deactivates their account
    form = CaptchaAuthenticationForm(request=None)
    with pytest.raises(ValidationError):
        form.confirm_login_allowed(user)
    user.refresh_from_db()
    assert user.is_active is False

    # Their lead clinician reactivates them via the user edit view
    client.force_login(lead_clinician)
    twofactor_signin(client, lead_clinician)
    response = client.post(
        reverse(
            "edit_epilepsy12_user",
            kwargs={
                "organisation_id": GOSH.pk,
                "epilepsy12_user_id": user.pk,
            },
        ),
        data={"delete": "true"},
    )

    assert response.status_code == HTTPStatus.FOUND

    user.refresh_from_db()
    assert user.is_active is True
    assert user.reactivated_at is not None

    # The reactivation is recorded in the audit log, attributed to the lead clinician
    reactivation_activity = (
        VisitActivity.objects.filter(
            epilepsy12user=user, activity=VisitActivity.CHANGED_ADMIN_FLAG
        )
        .order_by("-activity_datetime")
        .first()
    )
    assert reactivation_activity is not None
    assert "is_active: 'False' → 'True'" in reactivation_activity.details
    assert reactivation_activity.epilepsy12user_admin == lead_clinician

    # The inactivity check no longer flags them, so they can log in again
    assert is_inactive_beyond_deactivation_period(user) is False


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_user_deactivated_again_if_inactive_beyond_period_after_reactivation(
    e12_user_factory,
):
    """
    Reactivation restarts rather than disables the inactivity clock: a user
    who does not log in for another full period after being reactivated is
    deactivated again.
    """
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=timezone.now() - timedelta(days=900),
    )
    # Reactivated 800 days ago, and never logged in since
    user.reactivated_at = timezone.now() - timedelta(days=800)
    user.save()

    assert is_inactive_beyond_deactivation_period(user) is True


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_recent_reactivation_overrides_older_last_login(e12_user_factory):
    """
    The check measures from the most recent of last login and reactivation.
    """
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=timezone.now() - timedelta(days=900),
    )
    # Reactivated recently: the 900-day-old last login must not flag them
    user.reactivated_at = timezone.now() - timedelta(days=30)
    user.save()

    assert is_inactive_beyond_deactivation_period(user) is False


@pytest.mark.django_db
@override_settings(ACCOUNT_INACTIVITY_DEACTIVATION_PERIOD_DAYS=INACTIVITY_PERIOD_DAYS)
def test_deactivation_sets_reactivated_at_untouched(e12_user_factory):
    """
    Automatic deactivation must not set reactivated_at (only reactivation
    does); otherwise the deactivation itself would restart the clock.
    """
    user = e12_user_factory(
        role=AUDIT_CENTRE_CLINICIAN,
        last_login=timezone.now() - timedelta(days=800),
    )

    form = CaptchaAuthenticationForm(request=None)
    with pytest.raises(ValidationError):
        form.confirm_login_allowed(user)

    user.refresh_from_db()
    assert user.is_active is False
    assert user.reactivated_at is None