"""
Tests for which submit/unsubmit button renders in the case table, and when.

The submit/unsubmit button lives in
``templates/epilepsy12/partials/case_table.html`` and is gated by three
things:

- the template hierarchy: the button column renders when the audit is
  complete OR the case is locked (submitted). A locked-but-incomplete case
  must still show the unsubmit button so it can be unlocked and completed -
  https://github.com/rcpch/rcpch-audit-engine/issues/1492 (cohort 8 cases
  submitted before the genetic testing questions were added mid-cohort).
- the submission deadline: the button is disabled once
  ``days_remaining_before_submission == 0``.
- permissions: the button is disabled unless the user holds
  ``can_unlock_child_case_data_from_editing`` (locked case) or
  ``can_lock_child_case_data_from_editing`` (unlocked case).

The view-level lock/unlock workflow (who may POST ``case_submit``) is
characterised separately in
``epilepsy12/tests/view_tests/test_critical_workflow_characterisation.py``.

## Critical tests

[x] Locked + incomplete case still shows the unsubmit button (#1492 regression)
[x] Locked + incomplete case: button enabled for RCPCH audit team (has can_unlock)
[x] Locked + incomplete case: button disabled for view-only users (no can_unlock)
[x] Locked + complete case: enabled unsubmit button
[x] Locked case after the submission deadline: disabled even for RCPCH audit team
[x] Unlocked + complete case: enabled submit button for clinician (has can_lock)
[x] Unlocked + complete case: disabled submit button for view-only users (no can_lock)
[x] Unlocked + incomplete case: no submit button at all - progress bar instead
[x] Every <button> in the rendered table is closed (the unsubmit branch used to emit an unclosed <button>)

"""

# python imports
import re
from datetime import date, timedelta
from http import HTTPStatus

# third party imports
import pytest

# django imports
from django.urls import reverse

# E12 imports
from epilepsy12.models import Epilepsy12User, Organisation
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_rcpch_audit_team_data,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


# The submit/unsubmit button is the only place in any template that renders a
# cloud icon, so it can be located reliably in the rendered partial.
CLOUD_BUTTON_RE = re.compile(
    r"<button(?P<attrs>[^>]*)>\s*"
    r'<i class="cloud (?P<direction>download|upload) icon"></i>\s*'
    r"</button>",
    re.DOTALL,
)

# A recent first paediatric assessment date lands the case in the
# currently-open cohort, so the submission deadline has not passed. Cohort 4
# closed years ago (submission deadline January 2023) and is used for the
# closed-cohort test, matching test_permissions_closed_cohort.py.
OPEN_COHORT_FPA_DATE = date.today() - timedelta(days=30)
CLOSED_COHORT_FPA_DATE = date(2021, 6, 1)


def login(client, user_data):
    """Log in the seeded GOSH user for a role and verify them via 2FA."""
    user = Epilepsy12User.objects.get(
        first_name=user_data.role_str,
        is_active=True,
    )
    client.force_login(user)
    twofactor_signin(client, user)
    return user


def render_case_table(client, organisation):
    """GET the case table partial as an HTMX request (as the browser does
    after a submit/unsubmit), returning the decoded HTML."""
    response = client.get(
        reverse("cases", kwargs={"organisation_id": organisation.pk}),
        headers={"HX-Request": "true"},
    )
    assert response.status_code == HTTPStatus.OK
    return response.content.decode()


def cloud_buttons(html):
    """All submit/unsubmit buttons in the rendered table.

    Returns a list of (attrs, direction) tuples, where direction is
    "download" (unsubmit - case locked) or "upload" (submit - case unlocked).
    """
    return [
        (match.group("attrs"), match.group("direction"))
        for match in CLOUD_BUTTON_RE.finditer(html)
    ]


@pytest.mark.django_db
def test_locked_incomplete_case_shows_enabled_unsubmit_button_for_rcpch_audit_team(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """Regression test for #1492.

    A case locked (submitted) while its audit is incomplete - for example
    because new questions were added mid-cohort after submission - must
    still render the unsubmit button, enabled for a user holding
    ``can_unlock_child_case_data_from_editing``.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="locked_incomplete_child",
        organisations__organisation=GOSH,
        locked=True,
        registration__first_paediatric_assessment_date=OPEN_COHORT_FPA_DATE,
        registration__audit_progress__investigations_complete=False,
    )
    assert case.locked, "Case should be locked (submitted)"
    assert not case.registration.audit_progress.audit_complete, (
        "Case should be incomplete (the #1492 state)"
    )
    assert case.registration.days_remaining_before_submission > 0

    login(client, test_user_rcpch_audit_team_data)
    html = render_case_table(client, GOSH)

    buttons = cloud_buttons(html)
    assert len(buttons) == 1, (
        "Locked-but-incomplete case must still render the unsubmit button (#1492)"
    )
    attrs, direction = buttons[0]
    assert direction == "download", "Locked case must show the unsubmit icon"
    assert "disabled" not in attrs, (
        "RCPCH audit team (has can_unlock) should get an enabled unsubmit button"
    )
    assert "data-tooltip='Unsubmit to Epilepsy12'" in attrs


@pytest.mark.django_db
def test_locked_incomplete_case_shows_disabled_unsubmit_button_for_view_only_user(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """The #1492 locked-but-incomplete case shows the unsubmit button for a
    view-only user too, but disabled: the audit centre administrator group
    (TRUST_AUDIT_TEAM_VIEW_ONLY) holds neither the lock nor the unlock
    permission."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="locked_incomplete_view_only_child",
        organisations__organisation=GOSH,
        locked=True,
        registration__first_paediatric_assessment_date=OPEN_COHORT_FPA_DATE,
        registration__audit_progress__investigations_complete=False,
    )
    assert case.locked
    assert not case.registration.audit_progress.audit_complete

    login(client, test_user_audit_centre_administrator_data)
    html = render_case_table(client, GOSH)

    buttons = cloud_buttons(html)
    assert len(buttons) == 1, (
        "The unsubmit button should still render (disabled) for view-only users"
    )
    attrs, direction = buttons[0]
    assert direction == "download"
    assert "disabled" in attrs, (
        "View-only users (no can_unlock) must get a disabled unsubmit button"
    )
    assert "data-tooltip" not in attrs


@pytest.mark.django_db
def test_locked_complete_case_shows_enabled_unsubmit_button(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """A locked, audit-complete case in an open cohort shows the enabled
    unsubmit button for a user holding can_unlock."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="locked_complete_child",
        organisations__organisation=GOSH,
        locked=True,
        registration__first_paediatric_assessment_date=OPEN_COHORT_FPA_DATE,
    )
    assert case.locked
    assert case.registration.audit_progress.audit_complete
    assert case.registration.days_remaining_before_submission > 0

    login(client, test_user_rcpch_audit_team_data)
    html = render_case_table(client, GOSH)

    buttons = cloud_buttons(html)
    assert len(buttons) == 1
    attrs, direction = buttons[0]
    assert direction == "download"
    assert "disabled" not in attrs
    assert "data-tooltip='Unsubmit to Epilepsy12'" in attrs


@pytest.mark.django_db
def test_locked_case_unsubmit_button_disabled_after_submission_deadline(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """Once the submission deadline has passed (days_remaining == 0) the
    unsubmit button is disabled, even for the RCPCH audit team."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="locked_closed_cohort_child",
        organisations__organisation=GOSH,
        locked=True,
        registration__first_paediatric_assessment_date=CLOSED_COHORT_FPA_DATE,
        registration__audit_period__cohort_number=4,
    )
    assert case.locked
    assert case.registration.days_remaining_before_submission == 0

    login(client, test_user_rcpch_audit_team_data)
    html = render_case_table(client, GOSH)

    buttons = cloud_buttons(html)
    assert len(buttons) == 1, (
        "A locked case in a closed cohort still shows the (disabled) unsubmit button"
    )
    attrs, direction = buttons[0]
    assert direction == "download"
    assert "disabled" in attrs, (
        "The unsubmit button must be disabled once the deadline has passed"
    )
    assert "data-tooltip" not in attrs


@pytest.mark.django_db
def test_unlocked_complete_case_shows_enabled_submit_button_for_clinician(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """An unlocked, audit-complete case in an open cohort shows the enabled
    submit button for a clinician (TRUST_AUDIT_TEAM_EDIT_ACCESS holds
    ``can_lock_child_case_data_from_editing``)."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="unlocked_complete_child",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=OPEN_COHORT_FPA_DATE,
    )
    assert not case.locked
    assert case.registration.audit_progress.audit_complete
    assert case.registration.days_remaining_before_submission > 0

    login(client, test_user_audit_centre_clinician_data)
    html = render_case_table(client, GOSH)

    buttons = cloud_buttons(html)
    assert len(buttons) == 1
    attrs, direction = buttons[0]
    assert direction == "upload", "Unlocked case must show the submit icon"
    assert "disabled" not in attrs
    assert "data-tooltip='Submit to Epilepsy12'" in attrs


@pytest.mark.django_db
def test_unlocked_complete_case_shows_disabled_submit_button_for_view_only_user(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """The submit button renders disabled for view-only users: the audit
    centre administrator group holds no lock permission."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="unlocked_complete_view_only_child",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=OPEN_COHORT_FPA_DATE,
    )
    assert not case.locked
    assert case.registration.audit_progress.audit_complete

    login(client, test_user_audit_centre_administrator_data)
    html = render_case_table(client, GOSH)

    buttons = cloud_buttons(html)
    assert len(buttons) == 1
    attrs, direction = buttons[0]
    assert direction == "upload"
    assert "disabled" in attrs, (
        "View-only users (no can_lock) must get a disabled submit button"
    )
    assert "data-tooltip" not in attrs


@pytest.mark.django_db
def test_unlocked_incomplete_case_shows_no_submit_button(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """An unlocked, incomplete case shows no submit button at all - only the
    audit progress bar. (The button column is reserved for complete or
    locked cases.)"""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    case = e12_case_factory(
        first_name="unlocked_incomplete_child",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=OPEN_COHORT_FPA_DATE,
        registration__audit_progress__investigations_complete=False,
    )
    assert not case.locked
    assert not case.registration.audit_progress.audit_complete

    login(client, test_user_audit_centre_clinician_data)
    html = render_case_table(client, GOSH)

    assert cloud_buttons(html) == [], (
        "Unlocked, incomplete case must not render a submit/unsubmit button"
    )
    assert f"{case.pk}_audit_progress_bar" in html, (
        "The audit progress bar should render instead"
    )


@pytest.mark.django_db
def test_rendered_case_table_buttons_are_closed(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """Every <button> element in the rendered table must be closed.

    The unsubmit branch of the submit button used to emit an unclosed
    <button> (the closing tag only existed in the unlocked branch), so a
    locked case produced malformed HTML.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    e12_case_factory(
        first_name="button_balance_child",
        organisations__organisation=GOSH,
        locked=True,
        registration__first_paediatric_assessment_date=OPEN_COHORT_FPA_DATE,
    )

    login(client, test_user_rcpch_audit_team_data)
    html = render_case_table(client, GOSH)

    assert html.count("<button") == html.count("</button>"), (
        "Every <button> in the case table must have a matching closing tag"
    )
