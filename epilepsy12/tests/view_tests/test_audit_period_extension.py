"""
View tests for the audit period extension endpoint
(`audit_period_extension`).

Covers:
    - permission gating: only users holding `can_extend_submission_deadline`
      (the RCPCH audit team group) may GET the form or POST any action
    - POST extend: creates one extension row; a second POST updates the same
      row (one per organisation per audit period)
    - POST validation: missing/invalid days, invalid reason, ineligible cohort
    - POST close: sets the extension date to today with no reason
    - POST remove: deletes the row and reverts to the audit-wide deadline

NOTE these tests are date-sensitive: extend/close require today to be inside
an eligible (submitting or grace) cohort window. They use whichever cohort is
currently submitting and will need revisiting if the test clock ever moves past
that cohort's audit-wide deadline (cohort 8: 2027-01-12).
"""

from datetime import date, timedelta
from http import HTTPStatus

import pytest
from django.urls import reverse

from epilepsy12.models import (
    AuditPeriod,
    AuditPeriodExtension,
    Epilepsy12User,
    Organisation,
)
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_lead_clinician_data,
    test_user_rcpch_audit_team_data,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


EXTENSION_URL = "audit_period_extension"


def _submitting_cohort():
    period = AuditPeriod.objects.currently_submitting()
    assert period is not None, "No seeded cohort is currently submitting."
    return period


def _url(organisation, cohort):
    return reverse(
        EXTENSION_URL,
        kwargs={"organisation_id": organisation.pk, "cohort": cohort},
    )


def _audit_team_user():
    return Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )


def _lead_clinician():
    return Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )


def _sign_in(client, user, organisation):
    client.force_login(user)
    user.set_organisation_employer(
        organisation_employer=organisation, is_primary=True
    )
    twofactor_signin(client, user)


@pytest.mark.django_db
def test_get_form_allowed_for_audit_team(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """Audit team members can load the extension form partial."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)

    response = client.get(_url(GOSH, _submitting_cohort().cohort_number))

    assert response.status_code == HTTPStatus.OK
    assert b"Extend by" in response.content


@pytest.mark.django_db
def test_get_form_forbidden_for_lead_clinician(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """Organisation lead clinicians cannot load the extension form."""
    user = _lead_clinician()
    _sign_in(client, user, GOSH)

    response = client.get(_url(GOSH, _submitting_cohort().cohort_number))

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_post_extend_forbidden_for_lead_clinician(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """POSTs from users without the permission are refused and write nothing."""
    user = _lead_clinician()
    _sign_in(client, user, GOSH)
    period = _submitting_cohort()

    response = client.post(
        _url(GOSH, period.cohort_number), data={"days": 14, "reason": ""}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert not period.extensions.filter(organisation=GOSH).exists()


@pytest.mark.django_db
def test_post_extend_creates_extension(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """A valid POST creates the extension row with the expected date."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)
    period = _submitting_cohort()

    response = client.post(
        _url(GOSH, period.cohort_number), data={"days": 14, "reason": "0"}
    )

    assert response.status_code == HTTPStatus.OK
    extension = period.extensions.get(organisation=GOSH)
    assert extension.extended_submission_date == period.submission_deadline + timedelta(
        days=14
    )
    assert extension.reason == 0
    assert extension.created_by == user
    # card re-render shows the badge
    assert b"Extended to" in response.content


@pytest.mark.django_db
def test_post_extend_twice_updates_same_row(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """A second extension stacks on the first: still one row, date moved."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)
    period = _submitting_cohort()

    client.post(_url(GOSH, period.cohort_number), data={"days": 14, "reason": ""})
    client.post(_url(GOSH, period.cohort_number), data={"days": 7, "reason": ""})

    extensions = period.extensions.filter(organisation=GOSH)
    assert extensions.count() == 1
    assert extensions.first().extended_submission_date == (
        period.submission_deadline + timedelta(days=21)
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "post_data",
    [
        {"days": "", "reason": ""},          # missing days
        {"days": "not-a-number", "reason": ""},
        {"days": "0", "reason": ""},         # must be at least 1
        {"days": "-5", "reason": ""},
    ],
    ids=["missing", "not-a-number", "zero", "negative"],
)
def test_post_extend_invalid_days_rejected(
    client, seed_groups_fixture, seed_users_fixture, GOSH, post_data
):
    """Invalid days values re-render the form with an error; nothing is written."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)
    period = _submitting_cohort()

    response = client.post(_url(GOSH, period.cohort_number), data=post_data)

    assert response.status_code == HTTPStatus.OK
    assert b"valid number of days" in response.content
    assert not period.extensions.filter(organisation=GOSH).exists()


@pytest.mark.django_db
def test_post_extend_invalid_reason_rejected(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """A reason code outside the choices is rejected; nothing is written."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)
    period = _submitting_cohort()

    response = client.post(
        _url(GOSH, period.cohort_number), data={"days": 14, "reason": "99"}
    )

    assert response.status_code == HTTPStatus.OK
    assert b"Invalid reason" in response.content
    assert not period.extensions.filter(organisation=GOSH).exists()


@pytest.mark.django_db
def test_post_extend_recruiting_cohort_rejected(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """Extensions cannot be granted for the currently recruiting cohort."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)
    recruiting = AuditPeriod.objects.currently_recruiting()
    assert recruiting is not None, "No seeded cohort is currently recruiting."

    response = client.post(
        _url(GOSH, recruiting.cohort_number), data={"days": 14, "reason": ""}
    )

    assert response.status_code == HTTPStatus.OK
    assert b"submitting or grace cohort" in response.content
    assert not recruiting.extensions.filter(organisation=GOSH).exists()


@pytest.mark.django_db
def test_post_close_sets_today(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """Close action sets the extension date to today with no reason required."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)
    period = _submitting_cohort()

    response = client.post(_url(GOSH, period.cohort_number), data={"action": "close"})

    assert response.status_code == HTTPStatus.OK
    extension = period.extensions.get(organisation=GOSH)
    assert extension.extended_submission_date == date.today()
    assert extension.reason is None
    assert b"Closed early" in response.content


@pytest.mark.django_db
def test_post_remove_deletes_extension(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """Remove action deletes the row; the card reverts to the audit-wide date."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)
    period = _submitting_cohort()
    AuditPeriodExtension.objects.create(
        audit_period=period,
        organisation=GOSH,
        extended_submission_date=period.submission_deadline + timedelta(days=14),
        reason=0,
    )

    response = client.post(_url(GOSH, period.cohort_number), data={"action": "remove"})

    assert response.status_code == HTTPStatus.OK
    assert not period.extensions.filter(organisation=GOSH).exists()
    assert b"Extended to" not in response.content


@pytest.mark.django_db
def test_post_remove_without_extension_errors(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """Removing an extension that does not exist re-renders the form with an error."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)
    period = _submitting_cohort()

    response = client.post(_url(GOSH, period.cohort_number), data={"action": "remove"})

    assert response.status_code == HTTPStatus.OK
    assert b"no extension" in response.content


@pytest.mark.django_db
def test_unknown_cohort_returns_404(
    client, seed_groups_fixture, seed_users_fixture, GOSH
):
    """A cohort number with no AuditPeriod row is a 404."""
    user = _audit_team_user()
    _sign_in(client, user, GOSH)

    response = client.get(_url(GOSH, 999))

    assert response.status_code == HTTPStatus.NOT_FOUND
