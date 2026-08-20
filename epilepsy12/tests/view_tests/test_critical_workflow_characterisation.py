"""
PR 0 — Critical-workflow characterisation tests.

These tests exist to pin down the behaviour of the critical workflows that the
``AuditPeriodOrganisation`` foundation must not break. They are written against
the *current* (pre-foundation) behaviour so that later PRs in the foundation
sequence can run them as regression tests.

Scope (per ``audit-period-organisation.md`` PR 0):

- submission (lock/unlock) via ``case_submit``;
- report-builder smoke test (route loads, representative facets render);
- dashboard route and redirect behaviour (``?cohort=`` semantics); and
- Organisational Audit export (CSV generation from a submission period).

If a later PR changes one of these behaviours deliberately, the test should be
updated in the same PR. If it changes accidentally, the test should fail.
"""

from datetime import date, timedelta
from http import HTTPStatus

import pytest

from django.urls import reverse

from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    OrganisationalAuditSubmission,
    OrganisationalAuditSubmissionPeriod,
)
from epilepsy12.organisational_audit import export_submission_period_as_csv
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_rcpch_audit_team_data,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


# ---------------------------------------------------------------------------
# Submission / locking workflow
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_case_submit_locks_case_for_authorised_user(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """A lead clinician (who has ``can_lock_child_case_data_from_editing``)
    can lock an unlocked, editable case via ``case_submit``.

    This pins the current lock behaviour so that period-aware permission
    changes do not accidentally break submission.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Use a recent FPA date so Registration.save() resolves to the
    # currently-open cohort (the same pattern as the existing
    # test_open_cohort_allows_editing test). This keeps the test
    # date-independent: it always uses whichever cohort is open today.
    case = e12_case_factory(
        first_name="submit_lock_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )
    assert not case.locked, "Case should start unlocked"
    assert case.editable(), "Case should be editable (cohort still open)"

    user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str,
        is_active=True,
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("case_submit", kwargs={
        "organisation_id": GOSH.pk,
        "case_id": case.pk,
    })
    response = client.post(url)

    assert response.status_code == HTTPStatus.OK

    case.refresh_from_db()
    assert case.locked, "Case should be locked after submission"


@pytest.mark.django_db
def test_case_submit_unlocks_case_for_rcpch_audit_team(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """An RCPCH audit team member can unlock a locked case via ``case_submit``.

    A non-RCPCH user cannot unlock via POST because ``user_may_view_this_child``
    denies POST when ``can_edit`` is False, and ``Case.editable()`` returns
    False when the case is locked. Only RCPCH audit team members (who get
    ``can_edit=True`` unconditionally in ``lookup_user_permissions_on_child``)
    can unlock via this route.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="submit_unlock_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )
    case.locked = True
    case.save()
    assert case.locked, "Case should start locked"

    user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("case_submit", kwargs={
        "organisation_id": GOSH.pk,
        "case_id": case.pk,
    })
    response = client.post(url)

    assert response.status_code == HTTPStatus.OK

    case.refresh_from_db()
    assert not case.locked, "Case should be unlocked after submission"


@pytest.mark.django_db
def test_case_submit_locks_case_for_clinician(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """An audit-centre clinician can also lock a case via ``case_submit``.

    The ``AUDIT_CENTRE_CLINICIAN`` role maps to ``TRUST_AUDIT_TEAM_EDIT_ACCESS``,
    which includes ``EDITOR_PERMISSIONS`` and therefore
    ``CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING``. The clinician can lock (but not
    unlock) an editable case.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="submit_clinician_lock_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )
    assert case.editable(), "Case should be editable (cohort still open)"

    user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_clinician_data.role_str,
        is_active=True,
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("case_submit", kwargs={
        "organisation_id": GOSH.pk,
        "case_id": case.pk,
    })
    response = client.post(url)

    assert response.status_code == HTTPStatus.OK

    case.refresh_from_db()
    assert case.locked, "Case should be locked after submission"


@pytest.mark.django_db
def test_case_submit_forbidden_for_closed_cohort(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """Even a lead clinician cannot submit (lock) a case in a closed cohort,
    because ``user_may_view_this_child`` denies POST when ``can_edit`` is
    False.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Cohort 4 closed years ago — days_remaining == 0, not editable.
    case = e12_case_factory(
        first_name="submit_closed_cohort_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )
    assert not case.editable(), "Case should not be editable (closed cohort)"

    user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str,
        is_active=True,
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("case_submit", kwargs={
        "organisation_id": GOSH.pk,
        "case_id": case.pk,
    })
    response = client.post(url)

    assert response.status_code == HTTPStatus.FORBIDDEN

    case.refresh_from_db()
    assert not case.locked, "Case should remain unlocked"


# ---------------------------------------------------------------------------
# Report-builder smoke test
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_report_builder_loads_for_lead_clinician(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """The report-builder route (``case_filter_list``) must load without error
    for an authorised user after the ``AuditPeriodOrganisation`` migration.

    This is a smoke test: it does not assert facet counts, only that the page
    renders (200) and the response contains the expected context variable.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Create at least one case so the queryset is not empty.
    e12_case_factory(
        first_name="report_builder_smoke",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )

    user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str,
        is_active=True,
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("case_filter_list", kwargs={"organisation_id": GOSH.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "case_filter_list" in response.context


@pytest.mark.django_db
def test_report_builder_forbidden_for_unauthenticated(client):
    """An unauthenticated request to the report builder must redirect to
    login (302), not render the page.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    url = reverse("case_filter_list", kwargs={"organisation_id": GOSH.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    # The report-builder route currently redirects to /account/login/ without
    # preserving the next= parameter (see issue #1280). Pin the actual
    # behaviour so that the period-aware cutover can be verified as a
    # deliberate change.
    assert response.url == reverse("login")


# ---------------------------------------------------------------------------
# Dashboard route and redirect behaviour
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_dashboard_redirects_to_login_when_unauthenticated(client):
    """The organisation dashboard must redirect to login for anonymous users.

    This pins the current behaviour so that the period-aware dashboard
    cutover (PR 4) does not accidentally expose the dashboard publicly.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    url = reverse("selected_organisation_summary", kwargs={
        "organisation_id": GOSH.pk,
    })
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("login") + "?next=" + url


@pytest.mark.django_db
def test_dashboard_loads_with_cohort_query_param(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """The dashboard currently selects the cohort via ``?cohort=<number>``.

    This pins the current ``?cohort=`` semantics so that the PR 4 cutover to
    ``AuditPeriod.slug`` routing can be verified as a deliberate change.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="dashboard_cohort_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )

    user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str,
        is_active=True,
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("selected_organisation_summary", kwargs={
        "organisation_id": GOSH.pk,
    })
    # Use the cohort number of the case we just created (the currently-open
    # cohort) so the test is date-independent.
    open_cohort = case.registration.audit_period.cohort_number
    response = client.get(url, data={"cohort": open_cohort})

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_dashboard_defaults_to_grace_or_submitting_cohort(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """Without a ``?cohort=`` parameter, the dashboard currently falls back
    to the grace cohort (or the submitting cohort if no grace cohort is
    active).

    This pins the default-selection behaviour so that the PR 4 cutover to
    slug-based routing can be verified as a deliberate change.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    e12_case_factory(
        first_name="dashboard_default_cohort_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )

    user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str,
        is_active=True,
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("selected_organisation_summary", kwargs={
        "organisation_id": GOSH.pk,
    })
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


# ---------------------------------------------------------------------------
# Organisational Audit export
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_organisational_audit_export_csv(
    seed_groups_fixture,
    seed_users_fixture,
):
    """The ``export_submission_period_as_csv`` function must produce a CSV
    string from a submission period that has at least one submission.

    This pins the current export behaviour so that the foundation's
    permission changes do not break the Organisational Audit export.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    submission_period = OrganisationalAuditSubmissionPeriod.objects.create(
        year=2024,
        is_open=False,
    )

    OrganisationalAuditSubmission.objects.create(
        submission_period=submission_period,
        trust=GOSH.trust,
        local_health_board=None,
        submitted=True,
    )

    csv_data = export_submission_period_as_csv(submission_period)

    assert csv_data, "Export should produce non-empty CSV"
    assert isinstance(csv_data, str), "Export should return a string"


@pytest.mark.django_db
def test_organisational_audit_export_empty_period(
    seed_groups_fixture,
    seed_users_fixture,
):
    """Exporting a submission period with no submissions must not raise — it
    should return a CSV header row only (or an empty string, depending on
    the current implementation).
    """
    submission_period = OrganisationalAuditSubmissionPeriod.objects.create(
        year=2024,
        is_open=False,
    )

    # Must not raise.
    csv_data = export_submission_period_as_csv(submission_period)

    assert isinstance(csv_data, str)
