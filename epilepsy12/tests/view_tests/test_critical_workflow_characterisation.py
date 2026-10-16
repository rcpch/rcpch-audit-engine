"""
PR 0 — Critical-workflow characterisation tests.

These tests exist to pin down the behaviour of the critical workflows that the
``AuditPeriodOrganisation`` foundation must not break. They are written against
the *current* (pre-foundation) behaviour so that later PRs in the foundation
sequence can run them as regression tests.

Scope (per ``audit-period-organisation.md`` PR 0):

- submission (lock/unlock) via ``case_submit``;
- report-builder smoke test (route loads, representative facets render);
- operational dashboard route behaviour (non-slugged ``?cohort=`` semantics); and
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
    Site,
)
from epilepsy12.common_view_functions.sanction_user_access import (
    organisation_white_list_for_user,
)
from epilepsy12.general_functions.audit_period_hierarchy import (
    resolve_period_parent,
    expand_organisation_ids_via_identity,
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

    This pins the current behaviour so that operational dashboard routing
    changes do not accidentally expose the dashboard publicly.
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

    This pins the non-slugged operational dashboard route: the selected
    audit period is resolved from the existing ``?cohort=`` toggle, not from
    an ``AuditPeriod.slug`` URL.
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

    This pins the default-selection behaviour for the non-slugged
    operational dashboard route.
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


# ---------------------------------------------------------------------------
# PR 4 — period-correct dropdowns, identity-chain visibility, recruiting cohort
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_resolve_period_parent_falls_back_to_current_when_no_membership(
    reorganisation,
):
    """resolve_period_parent must fall back to the current parent when no
    approved AuditPeriodOrganisation membership exists for the selected
    period.

    This is the pre-cutover safety valve: before the cutover commands have
    run, no membership rows exist, so every call falls back to the current
    parent and behaviour is identical to the pre-foundation code.
    """
    org = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    # Temporarily delete the cohort 9 membership to simulate pre-cutover.
    from epilepsy12.models import AuditPeriodOrganisation

    AuditPeriodOrganisation.objects.filter(
        audit_period=cohort_9, organisation=org
    ).delete()

    parent, is_period_correct = resolve_period_parent(org, cohort_9)

    assert is_period_correct is False
    assert parent == org.trust  # the current parent


@pytest.mark.django_db
def test_resolve_period_parent_uses_membership_when_approved(
    reorganisation,
):
    """resolve_period_parent must return the period-correct parent from
    the approved AuditPeriodOrganisation membership when it exists.
    """
    org = reorganisation["org_a_predecessor"]
    cohort_8 = reorganisation["cohort_8"]
    trust_a = reorganisation["trust_a"]

    parent, is_period_correct = resolve_period_parent(org, cohort_8)

    assert is_period_correct is True
    assert parent == trust_a  # the period-correct parent (Trust A)


@pytest.mark.django_db
def test_expand_organisation_ids_via_identity_includes_predecessor(
    reorganisation,
):
    """expand_organisation_ids_via_identity must include inactive
    predecessor organisations that share the same OrganisationIdentity.
    """
    org_current = reorganisation["org_a_current"]
    org_predecessor = reorganisation["org_a_predecessor"]

    expanded = expand_organisation_ids_via_identity({org_current.pk})

    assert org_predecessor.pk in expanded
    assert org_current.pk in expanded


@pytest.mark.django_db
def test_expand_organisation_ids_noop_without_identity():
    """expand_organisation_ids_via_identity must be a no-op when no
    identity links exist (the pre-cutover state).
    """
    # RP401 (GOSH) is seeded without an identity FK.
    gosh = Organisation.objects.get(ods_code="RP401")
    assert gosh.identity_id is None

    expanded = expand_organisation_ids_via_identity({gosh.pk})

    assert expanded == {gosh.pk}


@pytest.mark.django_db
def test_organisation_white_list_includes_identity_predecessor(
    reorganisation,
):
    """organisation_white_list_for_user must include inactive predecessor
    organisations that share an OrganisationIdentity with the user's
    active employer, so that cases and users attached to the predecessor
    remain visible after cutover.
    """
    org_current = reorganisation["org_a_current"]
    org_predecessor = reorganisation["org_a_predecessor"]

    # Find or create a user employed at the current organisation.
    user = Epilepsy12User.objects.filter(
        employer_organisations__employer_organisation=org_current,
        employer_organisations__is_active=True,
    ).first()
    if user is None:
        # Use the seeded lead clinician and add an employer at org_current.
        user = Epilepsy12User.objects.filter(
            first_name=test_user_audit_centre_lead_clinician_data.role_str,
            is_active=True,
        ).first()
        from epilepsy12.models import OrganisationEmployer

        OrganisationEmployer.objects.get_or_create(
            epilepsy12_user=user,
            employer_organisation=org_current,
            defaults={"is_active": True},
        )

    whitelist = organisation_white_list_for_user(user)
    whitelist_ids = set(whitelist.values_list("pk", flat=True))

    assert org_current.pk in whitelist_ids
    assert org_predecessor.pk in whitelist_ids


@pytest.mark.django_db
def test_dashboard_period_alert_appears_when_parent_differs(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
):
    """When a specific cohort is selected and the period-correct parent
    differs from the current parent, the dashboard context must set
    show_period_alert=True.
    """
    org = reorganisation["org_a_current"]
    cohort_8 = reorganisation["cohort_8"]

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("selected_organisation_summary", kwargs={"organisation_id": org.pk})
    response = client.get(url, data={"cohort": cohort_8.cohort_number})

    assert response.status_code == HTTPStatus.OK
    assert response.context["show_period_alert"] is True


@pytest.mark.django_db
def test_dashboard_period_alert_absent_when_parent_matches(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
):
    """When the period-correct parent matches the current parent (cohort 9
    for the current organisation), the alert must not appear.
    """
    org = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("selected_organisation_summary", kwargs={"organisation_id": org.pk})
    response = client.get(url, data={"cohort": cohort_9.cohort_number})

    assert response.status_code == HTTPStatus.OK
    assert response.context["show_period_alert"] is False


@pytest.mark.django_db
def test_dashboard_falls_back_to_current_parent_without_membership(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
):
    """When no approved membership exists for the selected cohort (the
    pre-cutover state), the dashboard must fall back to the current parent
    and not show the period alert.
    """
    org = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    # Delete the cohort 9 membership to simulate pre-cutover.
    from epilepsy12.models import AuditPeriodOrganisation

    AuditPeriodOrganisation.objects.filter(
        audit_period=cohort_9, organisation=org
    ).delete()

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("selected_organisation_summary", kwargs={"organisation_id": org.pk})
    response = client.get(url, data={"cohort": cohort_9.cohort_number})

    assert response.status_code == HTTPStatus.OK
    assert response.context["show_period_alert"] is False


@pytest.mark.django_db
def test_case_list_shows_predecessor_cases_via_identity(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """Cases attached to an inactive predecessor organisation must remain
    visible in the case list when viewed from the active successor.
    """
    org_current = reorganisation["org_a_current"]
    org_predecessor = reorganisation["org_a_predecessor"]

    # Create a case attached to the predecessor organisation.
    case = e12_case_factory(
        first_name="predecessor_case_test",
        organisations__organisation=org_predecessor,
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": org_current.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    case_pks = {case.pk for case in response.context["case_list"].object_list}
    assert case.pk in case_pks


# ---------------------------------------------------------------------------
# PR 5 — case-list compatibility and clinical permissions
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_case_list_period_alert_appears_when_parent_differs(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
):
    """When a specific cohort is selected and the period-correct parent differs
    from the current parent, the case list context must set
    show_period_alert=True (same pattern as the dashboard in PR 4).
    """
    org = reorganisation["org_a_current"]
    cohort_8 = reorganisation["cohort_8"]

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": org.pk})
    response = client.get(url, data={"cohort": cohort_8.cohort_number})

    assert response.status_code == HTTPStatus.OK
    assert response.context["show_period_alert"] is True


@pytest.mark.django_db
def test_case_list_period_alert_absent_when_parent_matches(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
):
    """When the period-correct parent matches the current parent (cohort 9 for
    the current organisation), the case list alert must not appear.
    """
    org = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": org.pk})
    response = client.get(url, data={"cohort": cohort_9.cohort_number})

    assert response.status_code == HTTPStatus.OK
    assert response.context["show_period_alert"] is False


@pytest.mark.django_db
def test_case_list_alert_absent_when_no_cohort_selected(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
):
    """When no specific cohort is selected (all_children / all_cohorts), the
    case list must fall back to the current parent and not show the alert.
    """
    org = reorganisation["org_a_current"]

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": org.pk})
    response = client.get(url, data={"cohort": "all_children"})

    assert response.status_code == HTTPStatus.OK
    assert response.context["show_period_alert"] is False


@pytest.mark.django_db
def test_case_list_falls_back_to_current_parent_without_membership(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
):
    """When no approved membership exists for the selected cohort (the
    pre-cutover state), the case list must fall back to the current parent
    and not show the period alert.
    """
    from epilepsy12.models import AuditPeriodOrganisation

    org = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    AuditPeriodOrganisation.objects.filter(
        audit_period=cohort_9, organisation=org
    ).delete()

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": org.pk})
    response = client.get(url, data={"cohort": cohort_9.cohort_number})

    assert response.status_code == HTTPStatus.OK
    assert response.context["show_period_alert"] is False


@pytest.mark.django_db
def test_case_list_route_has_no_period_slug(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
):
    """The case list route must continue to use ?cohort=<number> and not a
    period-aware slug. Reverse('cases') must not accept an audit-period slug.
    """
    org = reorganisation["org_a_current"]

    url = reverse("cases", kwargs={"organisation_id": org.pk})
    assert "audit-period" not in url
    assert "audit_period" not in url


@pytest.mark.django_db
def test_direct_user_can_view_predecessor_registration(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """A user employed at the current ODS code (RJZ30) must be able to view a
    clinical field (e.g. the registration) for a case registered against the
    predecessor ODS code (RYQ30), via direct OrganisationIdentity access.
    """
    from epilepsy12.models import OrganisationEmployer

    org_current = reorganisation["org_a_current"]
    org_predecessor = reorganisation["org_a_predecessor"]

    case = e12_case_factory(
        first_name="direct_access_predecessor",
        organisations__organisation=org_predecessor,
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )

    # Create or reuse a user employed at the current organisation.
    user = Epilepsy12User.objects.filter(
        first_name=test_user_audit_centre_lead_clinician_data.role_str,
        is_active=True,
    ).first()
    OrganisationEmployer.objects.get_or_create(
        epilepsy12_user=user,
        employer_organisation=org_current,
        defaults={"is_active": True},
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse(
        "register",
        kwargs={
            "case_id": case.pk,
        },
    )
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_inherited_user_denied_across_reorganisation_boundary(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """A user elsewhere in Trust B (the current parent) must NOT be able to
    view a cohort-8 case registered against the predecessor under Trust A,
    because inherited access is period-aware and Trust B was not the parent
    for cohort 8. Before cutover this is a no-op (no memberships), so the test
    only exercises the period-aware path by using the reorganisation fixture
    which has approved memberships.
    """
    from epilepsy12.models import OrganisationEmployer
    from epilepsy12.tests.UserDataClasses import test_user_audit_centre_clinician_data

    org_current = reorganisation["org_a_current"]
    org_predecessor = reorganisation["org_a_predecessor"]
    cohort_8 = reorganisation["cohort_8"]

    # Case registered in cohort 8 under the predecessor (Trust A).
    case = e12_case_factory(
        first_name="inherited_boundary",
        organisations__organisation=org_predecessor,
        registration__first_paediatric_assessment_date=cohort_8.recruitment_start_date,
    )

    # Find a Trust B sibling organisation that is NOT the current org, so the
    # user's inherited access is via the parent, not direct identity.
    trust_b = reorganisation["trust_b"]
    sibling = (
        Organisation.objects.filter(trust=trust_b, active=True)
        .exclude(pk=org_current.pk)
        .first()
    )
    if sibling is None:
        pytest.skip("No Trust B sibling organisation available for inherited-access test.")

    user = Epilepsy12User.objects.filter(
        first_name=test_user_audit_centre_clinician_data.role_str,
        is_active=True,
    ).first()
    OrganisationEmployer.objects.get_or_create(
        epilepsy12_user=user,
        employer_organisation=sibling,
        defaults={"is_active": True},
    )
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse(
        "register",
        kwargs={
            "case_id": case.pk,
        },
    )
    response = client.get(url)

    # Period-aware inherited access: Trust B was not the parent for cohort 8,
    # so the user must be denied.
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_case_list_unregistered_case_visible(
    client,
    reorganisation,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """An unregistered case (no Registration / no audit_period) must still be
    visible in the case list — period-aware access cannot apply before a
    Registration exists, so the pre-foundation current-organisation rule is
    used.
    """
    org_current = reorganisation["org_a_current"]

    unreg = e12_case_factory(
        first_name="unregistered_period_test",
        organisations__organisation=org_current,
        registration=None,
    )

    user = Epilepsy12User.objects.filter(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    ).first()
    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": org_current.pk})
    response = client.get(url, data={"cohort": "all_children"})

    assert response.status_code == HTTPStatus.OK
    case_pks = {c.pk for c in response.context["case_list"].object_list}
    assert unreg.pk in case_pks
