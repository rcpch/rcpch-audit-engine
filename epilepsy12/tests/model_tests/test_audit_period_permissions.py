"""
Tests for the period-aware permission services.

These tests cover the PR 3 scope from ``audit-period-organisation.md``:

- direct Organisation A access to the agreed older in-flight periods;
- direct organisation access across an ODS code change (user employed at
  RJZ30 can access cases at RYQ30 for cohort 5, via shared
  ``OrganisationIdentity``);
- direct organisation access across a multi-step ODS code chain
  (RYQ30 -> RJZ30 -> RXZ40);
- Trust A inherited access before the move;
- Trust B inherited access from the effective period;
- denial for the opposite period in each Trust;
- RCPCH access;
- inactive employment;
- unregistered cases; and
- absence or ambiguity of required membership rows.

The tests use the ``reorganisation`` fixture from ``conftest.py``: PRUH moved
from Trust A (South London Healthcare NHS Trust, ``RYQ`` — dissolved) to
Trust B (King's College Hospital NHS Foundation Trust, ``RJZ`` — the live
seeded parent) at the cohort 8 -> 9 boundary, with an ODS code change at the
same boundary (``RYQ30`` -> ``RJZ30``) sharing one ``OrganisationIdentity``.
"""

from datetime import date

import pytest

from epilepsy12.general_functions.audit_period_permissions import (
    can_view_organisation_for_period,
    get_accessible_periods,
    get_accessible_memberships,
    get_accessible_organisations,
    can_view_case_for_period,
    can_edit_case_for_period,
    can_view_case_pre_registration,
    can_edit_case_pre_registration,
    CasePeriodMismatch,
)
from epilepsy12.models import (
    AuditPeriod,
    AuditPeriodOrganisation,
    Country,
    Epilepsy12User,
    Organisation,
    OrganisationEmployer,
    OrganisationIdentity,
    Trust,
)
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_LEAD_CLINICIAN,
    AUDIT_CENTRE_CLINICIAN,
    RCPCH_AUDIT_TEAM,
)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _make_user(
    *,
    email,
    role=AUDIT_CENTRE_CLINICIAN,
    is_active=True,
    email_confirmed=True,
    is_rcpch_audit_team_member=False,
    is_rcpch_staff=False,
    is_superuser=False,
    employers=None,
):
    """Create an Epilepsy12User with the given flags and active employments.

    Bypasses ``Epilepsy12UserManager.create_user`` because the manager forces
    ``is_active=False`` / ``email_confirmed=False`` and requires an
    ``organisation_employer`` argument (which would create an employer row we
    want to control explicitly). Instead we create the user row directly and
    attach ``OrganisationEmployer`` rows ourselves, mirroring the pattern in
    ``seed_users.py``.

    ``employers`` is an iterable of ``Organisation`` instances. Each becomes
    an active ``OrganisationEmployer`` row. If omitted (``None``), no
    employer row is created (used to test the no-employer denial path). Pass
    ``employers=[]`` for RCPCH staff who have no employer.
    """
    user = Epilepsy12User.objects.create(
        email=email,
        first_name=email.split("@")[0],
        surname="Test",
        role=role,
        is_active=is_active,
        email_confirmed=email_confirmed,
        is_rcpch_audit_team_member=is_rcpch_audit_team_member,
        is_rcpch_staff=is_rcpch_staff,
        is_superuser=is_superuser,
        password="pw",
    )
    if employers is not None:
        for org in employers:
            OrganisationEmployer.objects.create(
                epilepsy12_user=user,
                employer_organisation=org,
                is_primary=True,
                is_active=True,
                created_by=user,
            )
    return user


# ---------------------------------------------------------------------------
# Direct organisation access
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_direct_user_at_current_ods_code_can_view_both_periods(reorganisation):
    """A user employed at the current ODS code (RJZ30) can view PRUH's data
    for both cohort 8 (RYQ30, Trust A) and cohort 9 (RJZ30, Trust B).

    Direct access follows the organisation across all periods and ODS code
    changes via ``OrganisationIdentity``; it is not constrained by the
    period's Trust assignment.
    """
    org_a_current = reorganisation["org_a_current"]
    org_a_predecessor = reorganisation["org_a_predecessor"]
    cohort_8 = reorganisation["cohort_8"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="direct@kch.nhs.uk",
        employers=[org_a_current],
    )

    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is True
    # Direct access to the predecessor ODS code's cohort 8 data, via shared
    # OrganisationIdentity.
    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8) is True
    )


@pytest.mark.django_db
def test_direct_user_at_predecessor_ods_code_can_view_both_periods(reorganisation):
    """A user still employed at the predecessor ODS code (RYQ30) — for
    example a historical test user that was never migrated — can also view
    both periods, because RYQ30 shares the same ``OrganisationIdentity`` as
    RJZ30.

    This is the symmetric case: direct access is resolved through identity,
    not through which ODS code is "current".
    """
    org_a_current = reorganisation["org_a_current"]
    org_a_predecessor = reorganisation["org_a_predecessor"]
    cohort_8 = reorganisation["cohort_8"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="direct-predecessor@kch.nhs.uk",
        employers=[org_a_predecessor],
    )

    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8) is True
    )
    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is True


@pytest.mark.django_db
def test_direct_access_does_not_require_membership_row(reorganisation, cohort_5):
    """Direct organisation access does not require an approved
    ``AuditPeriodOrganisation`` row to exist for the (organisation, period)
    pair. The organisation itself always retains access to its own historical
    records; publication readiness is a separate consumer concern.

    Here the user is employed at RJZ30, but no membership row exists for
    (RJZ30, cohort 5). Direct access is still granted.
    """
    org_a_current = reorganisation["org_a_current"]

    user = _make_user(
        email="direct-no-membership@kch.nhs.uk",
        employers=[org_a_current],
    )

    assert (
        AuditPeriodOrganisation.objects.filter(
            organisation=org_a_current, audit_period=cohort_5
        ).exists()
        is False
    )
    assert can_view_organisation_for_period(user, org_a_current, cohort_5) is True


# ---------------------------------------------------------------------------
# Inherited Trust access — Trust A before the move, Trust B after
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_inherited_trust_a_user_can_view_cohort_8_not_cohort_9(reorganisation):
    """A user elsewhere in Trust A (current affiliation Trust A) can view
    PRUH's cohort 8 data (Trust A period) but not cohort 9 (Trust B period).

    Inherited access is current-affiliation-and-period-aware.
    """
    org_a_predecessor = reorganisation["org_a_predecessor"]
    org_a_current = reorganisation["org_a_current"]
    cohort_8 = reorganisation["cohort_8"]
    cohort_9 = reorganisation["cohort_9"]
    trust_a = reorganisation["trust_a"]

    # A sibling organisation under Trust A — the user is employed here, so
    # their current affiliation is Trust A. Use a fresh organisation under
    # the dissolved trust so the user's current parent is Trust A.
    sibling_under_trust_a = Organisation.objects.create(
        ods_code="RYQ99",
        name="Sibling Hospital under Trust A",
        trust=trust_a,
        country=reorganisation["country"],
        active=True,
    )

    user = _make_user(
        email="inherited-a@trust-a.nhs.uk",
        employers=[sibling_under_trust_a],
    )

    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8)
        is True
    )
    # Cohort 9 membership assigns PRUH to Trust B, not Trust A. The user's
    # current affiliation is Trust A, so inherited access is denied.
    assert (
        can_view_organisation_for_period(user, org_a_current, cohort_9) is False
    )


@pytest.mark.django_db
def test_inherited_trust_b_user_can_view_cohort_9_not_cohort_8(reorganisation):
    """A user elsewhere in Trust B (current affiliation Trust B) can view
    PRUH's cohort 9 data (Trust B period) but not cohort 8 (Trust A period).

    This is the key asymmetry: even though PRUH itself can see both periods,
    a Trust B sibling can only see the period in which PRUH was assigned to
    Trust B.
    """
    org_a_predecessor = reorganisation["org_a_predecessor"]
    org_a_current = reorganisation["org_a_current"]
    cohort_8 = reorganisation["cohort_8"]
    cohort_9 = reorganisation["cohort_9"]

    # A sibling organisation under Trust B (King's). RJZ01 (King's College
    # Hospital) is seeded under RJZ, so the user's current affiliation is
    # Trust B.
    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")

    user = _make_user(
        email="inherited-b@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is True
    # Cohort 8 membership assigns PRUH (RYQ30) to Trust A, not Trust B.
    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8)
        is False
    )


# ---------------------------------------------------------------------------
# RCPCH access
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_rcpch_audit_team_member_can_view_any_period(reorganisation):
    """An authorised RCPCH audit team member retains broader access that is
    not constrained by the period-aware affiliation rules."""
    org_a_predecessor = reorganisation["org_a_predecessor"]
    org_a_current = reorganisation["org_a_current"]
    cohort_8 = reorganisation["cohort_8"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="rcpch@rcpch.ac.uk",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        employers=[],  # RCPCH staff need no employer
    )

    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8)
        is True
    )
    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is True


@pytest.mark.django_db
def test_rcpch_superuser_can_view_any_period(reorganisation):
    """A superuser retains broader access."""
    org_a_current = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="superuser@rcpch.ac.uk",
        role=RCPCH_AUDIT_TEAM,
        is_superuser=True,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        employers=[],
    )

    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is True


# ---------------------------------------------------------------------------
# Inactive employment / unconfirmed email
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_inactive_employment_denies_access(reorganisation):
    """A user whose employment is marked inactive is denied access, even if
    they are employed at the organisation."""
    org_a_current = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="inactive@kch.nhs.uk",
        employers=[org_a_current],
    )
    # Mark the employment inactive.
    OrganisationEmployer.objects.filter(
        epilepsy12_user=user, employer_organisation=org_a_current
    ).update(is_active=False)

    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is False


@pytest.mark.django_db
def test_inactive_user_account_denies_access(reorganisation):
    """A user whose account is inactive is denied access."""
    org_a_current = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="inactive-account@kch.nhs.uk",
        is_active=False,
        employers=[org_a_current],
    )

    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is False


@pytest.mark.django_db
def test_unconfirmed_email_denies_access(reorganisation):
    """A user who has not confirmed their email is denied access (unless a
    superuser, which is tested separately).

    ``Epilepsy12User.save()`` forces ``email_confirmed=True`` whenever the
    user has a usable password, so to test the unconfirmed state we create
    the user with an unusable password (``set_unusable_password``) and then
    persist ``email_confirmed=False`` via a queryset update (bypassing
    ``save()``). This mirrors the real state of a newly-created user who
    has not yet clicked the confirmation link.
    """
    org_a_current = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="unconfirmed@kch.nhs.uk",
        email_confirmed=False,
        employers=[org_a_current],
    )
    # The helper sets a usable password, which save() would have used to
    # force email_confirmed=True. Bypass save() to persist the unconfirmed
    # state directly, matching a real pre-confirmation user row.
    Epilepsy12User.objects.filter(pk=user.pk).update(email_confirmed=False)
    user.refresh_from_db()

    assert user.email_confirmed is False
    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is False


# ---------------------------------------------------------------------------
# Absence or ambiguity of membership rows
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_inherited_access_denied_when_membership_missing(reorganisation, cohort_5):
    """Inherited access is denied when no ``AuditPeriodOrganisation`` row
    exists for the (organisation, period) pair. There is no fallback to
    current relationships.

    Here a Trust B sibling tries to view PRUH for cohort 5, which has no
    membership row. Inherited access is denied.
    """
    org_a_current = reorganisation["org_a_current"]
    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")

    user = _make_user(
        email="inherited-b-no-membership@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    assert (
        AuditPeriodOrganisation.objects.filter(
            organisation=org_a_current, audit_period=cohort_5
        ).exists()
        is False
    )
    assert can_view_organisation_for_period(user, org_a_current, cohort_5) is False


@pytest.mark.django_db
def test_inherited_access_denied_when_membership_unapproved(reorganisation):
    """Inherited access is denied when the membership row exists but has not
    been approved. There is no fallback to current relationships.

    Here a Trust B sibling tries to view PRUH for a period where the
    membership row is unapproved.
    """
    org_a_current = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]
    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")

    # Mark the cohort 9 membership unapproved.
    membership = AuditPeriodOrganisation.objects.get(
        organisation=org_a_current, audit_period=cohort_9
    )
    membership.approved_at = None
    membership.save(update_fields=["approved_at"])

    user = _make_user(
        email="inherited-b-unapproved@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is False


@pytest.mark.django_db
def test_unrelated_user_denied(reorganisation):
    """A user with no affiliation to the organisation or its parents is
    denied access to all periods."""
    org_a_current = reorganisation["org_a_current"]
    org_a_predecessor = reorganisation["org_a_predecessor"]
    cohort_8 = reorganisation["cohort_8"]
    cohort_9 = reorganisation["cohort_9"]

    # Addenbrooke's is seeded under RGT (Cambridge), unrelated to PRUH.
    unrelated_org = Organisation.objects.get(ods_code="RGT01")

    user = _make_user(
        email="unrelated@addenbrookes.nhs.uk",
        employers=[unrelated_org],
    )

    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is False
    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8) is False
    )


@pytest.mark.django_db
def test_user_with_no_employer_denied(reorganisation):
    """A user with no active employer is denied access (unless RCPCH)."""
    org_a_current = reorganisation["org_a_current"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="no-employer@example.com",
        employers=[],
    )

    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is False


# ---------------------------------------------------------------------------
# get_accessible_periods
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_get_accessible_periods_direct_user_sees_all_participating_periods(
    reorganisation,
):
    """A direct user (employed at RJZ30) sees every period PRUH participated
    in — both cohort 8 (RYQ30, Trust A) and cohort 9 (RJZ30, Trust B).

    Direct access is period-independent in principle, but the
    accessible-periods query returns only periods with an approved,
    included membership row (a period with no membership has no dashboard
    summary to show).
    """
    org_a_current = reorganisation["org_a_current"]
    cohort_8 = reorganisation["cohort_8"]
    cohort_9 = reorganisation["cohort_9"]

    user = _make_user(
        email="periods-direct@kch.nhs.uk",
        employers=[org_a_current],
    )

    periods = list(get_accessible_periods(user, org_a_current))
    cohort_numbers = {p.cohort_number for p in periods}
    assert cohort_numbers == {8, 9}


@pytest.mark.django_db
def test_get_accessible_periods_inherited_trust_a_user_sees_only_cohort_8(
    reorganisation,
):
    """An inherited Trust A user sees only cohort 8 (the period in which PRUH
    was assigned to Trust A). Cohort 9 (Trust B) is excluded."""
    org_a_predecessor = reorganisation["org_a_predecessor"]
    trust_a = reorganisation["trust_a"]

    sibling_under_trust_a = Organisation.objects.create(
        ods_code="RYQ99",
        name="Sibling Hospital under Trust A",
        trust=trust_a,
        country=reorganisation["country"],
        active=True,
    )

    user = _make_user(
        email="periods-inherited-a@trust-a.nhs.uk",
        employers=[sibling_under_trust_a],
    )

    periods = list(get_accessible_periods(user, org_a_predecessor))
    cohort_numbers = {p.cohort_number for p in periods}
    assert cohort_numbers == {8}


@pytest.mark.django_db
def test_get_accessible_periods_inherited_trust_b_user_sees_only_cohort_9(
    reorganisation,
):
    """An inherited Trust B user sees only cohort 9 (the period in which PRUH
    was assigned to Trust B). Cohort 8 (Trust A) is excluded."""
    org_a_current = reorganisation["org_a_current"]
    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")

    user = _make_user(
        email="periods-inherited-b@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    periods = list(get_accessible_periods(user, org_a_current))
    cohort_numbers = {p.cohort_number for p in periods}
    assert cohort_numbers == {9}


@pytest.mark.django_db
def test_get_accessible_periods_inherited_resolves_identity_chain(
    reorganisation,
):
    """An inherited Trust A user passing the current ODS code (RJZ30) still
    sees cohort 8, because the membership for cohort 8 is held against the
    predecessor RYQ30 which shares the same ``OrganisationIdentity``.

    This mirrors how the dashboard will call the function: it always passes
    the current organisation, and the service resolves the identity chain
    to find historical memberships.
    """
    org_a_current = reorganisation["org_a_current"]  # RJZ30 (current)
    trust_a = reorganisation["trust_a"]

    sibling_under_trust_a = Organisation.objects.create(
        ods_code="RYQ98",
        name="Sibling Hospital under Trust A (chain)",
        trust=trust_a,
        country=reorganisation["country"],
        active=True,
    )

    user = _make_user(
        email="periods-inherited-a-chain@trust-a.nhs.uk",
        employers=[sibling_under_trust_a],
    )

    periods = list(get_accessible_periods(user, org_a_current))
    cohort_numbers = {p.cohort_number for p in periods}
    assert cohort_numbers == {8}


@pytest.mark.django_db
def test_get_accessible_periods_rcpch_user_sees_all_participating_periods(
    reorganisation,
):
    """An RCPCH user sees every period PRUH participated in."""
    org_a_current = reorganisation["org_a_current"]

    user = _make_user(
        email="periods-rcpch@rcpch.ac.uk",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        employers=[],
    )

    periods = list(get_accessible_periods(user, org_a_current))
    cohort_numbers = {p.cohort_number for p in periods}
    assert cohort_numbers == {8, 9}


@pytest.mark.django_db
def test_get_accessible_periods_unrelated_user_sees_none(reorganisation):
    """An unrelated user sees no periods for PRUH."""
    org_a_current = reorganisation["org_a_current"]
    unrelated_org = Organisation.objects.get(ods_code="RGT01")

    user = _make_user(
        email="periods-unrelated@addenbrookes.nhs.uk",
        employers=[unrelated_org],
    )

    periods = list(get_accessible_periods(user, org_a_current))
    assert periods == []


# ---------------------------------------------------------------------------
# get_accessible_memberships
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_get_accessible_memberships_rcpch_user_sees_all_for_period(
    reorganisation, england_hierarchy
):
    """An RCPCH user sees every approved, included membership for the period."""
    cohort_9 = reorganisation["cohort_9"]
    org_a_current = reorganisation["org_a_current"]

    # Add a sibling organisation under Trust B for cohort 9 so the RCPCH
    # user sees more than one membership.
    kings = Organisation.objects.get(ods_code="RJZ01")
    AuditPeriodOrganisation.objects.update_or_create(
        audit_period=cohort_9,
        organisation=kings,
        defaults={
            "country": england_hierarchy["country"],
            "trust": reorganisation["trust_b"],
            "integrated_care_board": kings.integrated_care_board,
            "nhs_england_region": kings.nhs_england_region,
            "openuk_network": kings.openuk_network,
            "included_in_reporting": True,
            "approved_at": date(2028, 1, 1),
            "source": "snapshot",
        },
    )

    user = _make_user(
        email="memberships-rcpch@rcpch.ac.uk",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        employers=[],
    )

    memberships = list(get_accessible_memberships(user, cohort_9))
    org_ids = {m.organisation_id for m in memberships}
    assert org_a_current.id in org_ids
    assert kings.id in org_ids


@pytest.mark.django_db
def test_get_accessible_memberships_inherited_trust_b_user_sees_trust_b_orgs(
    reorganisation, england_hierarchy
):
    """An inherited Trust B user sees only cohort-9 memberships whose Trust
    is Trust B. PRUH (RJZ30, Trust B) is included; a Trust A organisation
    is not.
    """
    cohort_9 = reorganisation["cohort_9"]
    org_a_current = reorganisation["org_a_current"]
    trust_a = reorganisation["trust_a"]

    # A Trust A organisation with a cohort 9 membership — must NOT appear.
    trust_a_org = Organisation.objects.create(
        ods_code="RYQ98",
        name="Trust A Hospital (cohort 9)",
        trust=trust_a,
        country=england_hierarchy["country"],
        active=True,
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_9,
        organisation=trust_a_org,
        country=england_hierarchy["country"],
        trust=trust_a,
        approved_at=date(2028, 1, 1),
    )

    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")
    user = _make_user(
        email="memberships-inherited-b@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    memberships = list(get_accessible_memberships(user, cohort_9))
    org_ids = {m.organisation_id for m in memberships}
    assert org_a_current.id in org_ids  # PRUH under Trust B
    assert trust_a_org.id not in org_ids  # Trust A org excluded


@pytest.mark.django_db
def test_get_accessible_memberships_direct_user_sees_own_org_across_identity_chain(
    reorganisation,
):
    """A direct user employed at RJZ30 sees their own organisation's
    memberships across the identity chain — both cohort 8 (RYQ30) and
    cohort 9 (RJZ30) — because both share the same OrganisationIdentity.

    This is the bulk-query equivalent of direct access across an ODS code
    change: the user's direct organisation set includes RYQ30 via the shared
    identity, so the cohort 8 membership for RYQ30 is returned.
    """
    cohort_8 = reorganisation["cohort_8"]
    org_a_predecessor = reorganisation["org_a_predecessor"]
    org_a_current = reorganisation["org_a_current"]

    user = _make_user(
        email="memberships-direct@kch.nhs.uk",
        employers=[org_a_current],
    )

    # Cohort 8 membership is for RYQ30 (the predecessor), not RJZ30. A
    # direct user at RJZ30 should still see it via the shared identity.
    memberships = list(get_accessible_memberships(user, cohort_8))
    org_ids = {m.organisation_id for m in memberships}
    assert org_a_predecessor.id in org_ids


# ---------------------------------------------------------------------------
# get_accessible_organisations
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_get_accessible_organisations_rcpch_user_sees_all_for_period(
    reorganisation, england_hierarchy
):
    """An RCPCH user sees every organisation with an approved, included
    membership for the period."""
    cohort_9 = reorganisation["cohort_9"]
    org_a_current = reorganisation["org_a_current"]

    kings = Organisation.objects.get(ods_code="RJZ01")
    AuditPeriodOrganisation.objects.update_or_create(
        audit_period=cohort_9,
        organisation=kings,
        defaults={
            "country": england_hierarchy["country"],
            "trust": reorganisation["trust_b"],
            "integrated_care_board": kings.integrated_care_board,
            "nhs_england_region": kings.nhs_england_region,
            "openuk_network": kings.openuk_network,
            "included_in_reporting": True,
            "approved_at": date(2028, 1, 1),
            "source": "snapshot",
        },
    )

    user = _make_user(
        email="orgs-rcpch@rcpch.ac.uk",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        employers=[],
    )

    orgs = list(get_accessible_organisations(user, cohort_9))
    ods_codes = {o.ods_code for o in orgs}
    assert "RJZ30" in ods_codes  # PRUH
    assert "RJZ01" in ods_codes  # King's


@pytest.mark.django_db
def test_get_accessible_organisations_inherited_trust_b_user_sees_trust_b_orgs(
    reorganisation, england_hierarchy
):
    """An inherited Trust B user sees only cohort-9 organisations under
    Trust B. A Trust A organisation with a cohort 9 membership is excluded."""
    cohort_9 = reorganisation["cohort_9"]
    org_a_current = reorganisation["org_a_current"]
    trust_a = reorganisation["trust_a"]

    trust_a_org = Organisation.objects.create(
        ods_code="RYQ97",
        name="Trust A Hospital (cohort 9 orgs)",
        trust=trust_a,
        country=england_hierarchy["country"],
        active=True,
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_9,
        organisation=trust_a_org,
        country=england_hierarchy["country"],
        trust=trust_a,
        approved_at=date(2028, 1, 1),
    )

    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")
    user = _make_user(
        email="orgs-inherited-b@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    orgs = list(get_accessible_organisations(user, cohort_9))
    ods_codes = {o.ods_code for o in orgs}
    assert "RJZ30" in ods_codes  # PRUH under Trust B
    assert "RYQ97" not in ods_codes  # Trust A org excluded


@pytest.mark.django_db
def test_get_accessible_organisations_with_parent_filter(
    reorganisation, england_hierarchy
):
    """The ``parent`` filter narrows the result to organisations whose
    membership for the period assigns them to that parent.

    Here an RCPCH user requests cohort 9 organisations under Trust B. PRUH
    (RJZ30, Trust B) is included; a Trust A organisation is not.
    """
    cohort_9 = reorganisation["cohort_9"]
    trust_a = reorganisation["trust_a"]
    trust_b = reorganisation["trust_b"]

    trust_a_org = Organisation.objects.create(
        ods_code="RYQ96",
        name="Trust A Hospital (parent filter)",
        trust=trust_a,
        country=england_hierarchy["country"],
        active=True,
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_9,
        organisation=trust_a_org,
        country=england_hierarchy["country"],
        trust=trust_a,
        approved_at=date(2028, 1, 1),
    )

    user = _make_user(
        email="orgs-parent-filter@rcpch.ac.uk",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        employers=[],
    )

    orgs = list(get_accessible_organisations(user, cohort_9, parent=trust_b))
    ods_codes = {o.ods_code for o in orgs}
    assert "RJZ30" in ods_codes  # PRUH under Trust B
    assert "RYQ96" not in ods_codes  # Trust A org excluded by parent filter


@pytest.mark.django_db
def test_get_accessible_organisations_direct_user_sees_own_org_across_identity_chain(
    reorganisation,
):
    """A direct user employed at RJZ30 sees their own organisation for cohort
    8 (RYQ30, the predecessor) via the shared identity chain, even though
    they have no inherited access to Trust A.
    """
    cohort_8 = reorganisation["cohort_8"]
    org_a_predecessor = reorganisation["org_a_predecessor"]
    org_a_current = reorganisation["org_a_current"]

    user = _make_user(
        email="orgs-direct-chain@kch.nhs.uk",
        employers=[org_a_current],
    )

    orgs = list(get_accessible_organisations(user, cohort_8))
    ods_codes = {o.ods_code for o in orgs}
    assert "RYQ30" in ods_codes  # predecessor via identity chain


# ---------------------------------------------------------------------------
# Direct access across a multi-step ODS code chain (RYQ30 -> RJZ30 -> RXZ40)
# ---------------------------------------------------------------------------
#
# The PR 3 scope calls out the multi-step succession chain explicitly. The
# scenario: PRUH changes its ODS code a second time (RJZ30 -> RXZ40) at the
# cohort 9 -> 10 boundary, joining a new dissolved Trust C (RXZ). All three
# Organisation rows (RYQ30, RJZ30, RXZ40) share the same OrganisationIdentity.
#
# A user employed at the latest ODS code (RXZ40) must be able to view PRUH's
# data for all three periods: cohort 8 (RYQ30, Trust A), cohort 9 (RJZ30,
# Trust B) and cohort 10 (RXZ40, Trust C). Direct access follows the
# organisation across all periods and ODS code changes via the identity chain.


@pytest.fixture
def multi_step_chain(reorganisation):
    """Extend the ``reorganisation`` fixture with a third ODS code (RXZ40)
    and a cohort 10 membership, forming the three-step chain
    RYQ30 -> RJZ30 -> RXZ40.

    Returns a dict with the new keys added to the ``reorganisation`` dict:
        trust_c:              dissolved Trust (RXZ), ``active=False``
        org_a_successor:      successor Organisation (RXZ40), ``active=True``
        cohort_10:            the cohort 10 AuditPeriod
        cohort_10_membership: approved AuditPeriodOrganisation for cohort 10
    """
    england = reorganisation["country"]
    org_a_identity = reorganisation["org_a_identity"]

    # Trust C — a hypothetical future successor trust (RXZ), dissolved.
    trust_c, _ = Trust.objects.get_or_create(
        ods_code="RXZ",
        defaults={
            "name": "FUTURE SUCCESSOR TRUST (RXZ)",
            "town": "ORPINGTON",
            "postcode": "BR6 8ND",
            "country": "ENGLAND",
            "active": False,
        },
    )

    # The third ODS code (RXZ40) — the latest successor, active.
    org_a_successor, _ = Organisation.objects.get_or_create(
        ods_code="RXZ40",
        defaults={
            "name": "PRINCESS ROYAL UNIVERSITY HOSPITAL (RXZ40)",
            "trust": trust_c,
            "country": england,
            "identity": org_a_identity,
            "active": True,
        },
    )
    if org_a_successor.identity_id != org_a_identity.id:
        org_a_successor.identity = org_a_identity
        org_a_successor.save(update_fields=["identity"])

    # Cohort 10 is not seeded (only 4-9 are). Create it with derived dates.
    cohort_10, _ = AuditPeriod.objects.get_or_create(
        cohort_number=10,
        defaults={
            "name": "Cohort 10",
            "recruitment_start_date": date(2027, 1, 1),
            "recruitment_end_date": date(2027, 12, 31),
            "data_collection_end_date": date(2028, 12, 31),
            "submission_deadline": date(2029, 1, 9),
            "slug": "cohort-10",
            "is_visible": False,
        },
    )

    cohort_10_membership, _ = AuditPeriodOrganisation.objects.update_or_create(
        audit_period=cohort_10,
        organisation=org_a_successor,
        defaults={
            "country": england,
            "trust": trust_c,
            "local_health_board": None,
            "integrated_care_board": None,
            "nhs_england_region": None,
            "openuk_network": None,
            "included_in_reporting": True,
            "approved_at": date(2029, 1, 1),
            "source": "manual",
            "notes": "Multi-step chain canary: PRUH under Trust C (RXZ) for cohort 10.",
        },
    )

    return {
        **reorganisation,
        "trust_c": trust_c,
        "org_a_successor": org_a_successor,
        "cohort_10": cohort_10,
        "cohort_10_membership": cohort_10_membership,
    }


@pytest.mark.django_db
def test_multi_step_chain_can_view_all_three_periods(multi_step_chain):
    """A user employed at the latest ODS code (RXZ40) can view PRUH's data
    for all three periods: cohort 8 (RYQ30, Trust A), cohort 9 (RJZ30,
    Trust B) and cohort 10 (RXZ40, Trust C).

    Direct access follows the organisation across all periods and ODS code
    changes via the shared ``OrganisationIdentity``.
    """
    org_a_predecessor = multi_step_chain["org_a_predecessor"]  # RYQ30
    org_a_current = multi_step_chain["org_a_current"]  # RJZ30
    org_a_successor = multi_step_chain["org_a_successor"]  # RXZ40
    cohort_8 = multi_step_chain["cohort_8"]
    cohort_9 = multi_step_chain["cohort_9"]
    cohort_10 = multi_step_chain["cohort_10"]

    user = _make_user(
        email="chain-latest@pruh.nhs.uk",
        employers=[org_a_successor],
    )

    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8)
        is True
    )
    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is True
    assert can_view_organisation_for_period(user, org_a_successor, cohort_10) is True


@pytest.mark.django_db
def test_multi_step_chain_user_at_middle_code_can_view_all_three_periods(
    multi_step_chain,
):
    """A user employed at the middle ODS code (RJZ30) can also view all three
    periods, because RJZ30 shares the same ``OrganisationIdentity`` as both
    RYQ30 and RXZ40.

    This is the symmetric case: direct access is resolved through identity,
    not through which ODS code is "current" or "latest".
    """
    org_a_predecessor = multi_step_chain["org_a_predecessor"]  # RYQ30
    org_a_current = multi_step_chain["org_a_current"]  # RJZ30
    org_a_successor = multi_step_chain["org_a_successor"]  # RXZ40
    cohort_8 = multi_step_chain["cohort_8"]
    cohort_9 = multi_step_chain["cohort_9"]
    cohort_10 = multi_step_chain["cohort_10"]

    user = _make_user(
        email="chain-middle@kch.nhs.uk",
        employers=[org_a_current],
    )

    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8)
        is True
    )
    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is True
    assert can_view_organisation_for_period(user, org_a_successor, cohort_10) is True


@pytest.mark.django_db
def test_multi_step_chain_get_accessible_periods_sees_all_three(multi_step_chain):
    """``get_accessible_periods`` for a direct user at RXZ40 returns all three
    periods (8, 9, 10), resolved across the full identity chain.
    """
    org_a_successor = multi_step_chain["org_a_successor"]  # RXZ40

    user = _make_user(
        email="chain-periods@pruh.nhs.uk",
        employers=[org_a_successor],
    )

    periods = list(get_accessible_periods(user, org_a_successor))
    cohort_numbers = {p.cohort_number for p in periods}
    assert cohort_numbers == {8, 9, 10}


@pytest.mark.django_db
def test_multi_step_chain_get_accessible_organisations_sees_all_three(
    multi_step_chain,
):
    """``get_accessible_organisations`` for a direct user at RXZ40 returns the
    PRUH organisation for each period — RYQ30 for cohort 8, RJZ30 for cohort
    9, RXZ40 for cohort 10 — resolved across the full identity chain.
    """
    cohort_8 = multi_step_chain["cohort_8"]
    cohort_9 = multi_step_chain["cohort_9"]
    cohort_10 = multi_step_chain["cohort_10"]
    org_a_successor = multi_step_chain["org_a_successor"]  # RXZ40

    user = _make_user(
        email="chain-orgs@pruh.nhs.uk",
        employers=[org_a_successor],
    )

    orgs_8 = {o.ods_code for o in get_accessible_organisations(user, cohort_8)}
    orgs_9 = {o.ods_code for o in get_accessible_organisations(user, cohort_9)}
    orgs_10 = {o.ods_code for o in get_accessible_organisations(user, cohort_10)}

    assert "RYQ30" in orgs_8
    assert "RJZ30" in orgs_9
    assert "RXZ40" in orgs_10


@pytest.mark.django_db
def test_multi_step_chain_inherited_does_not_cross_chain(multi_step_chain):
    """Inherited access never crosses the succession chain to a historical
    parent — that is direct access only.

    A user elsewhere in Trust C (the cohort 10 parent) can view PRUH for
    cohort 10 (RXZ40, Trust C) but NOT for cohort 8 (RYQ30, Trust A) or
    cohort 9 (RJZ30, Trust B), even though all three share the same
    ``OrganisationIdentity``.
    """
    org_a_predecessor = multi_step_chain["org_a_predecessor"]  # RYQ30
    org_a_current = multi_step_chain["org_a_current"]  # RJZ30
    org_a_successor = multi_step_chain["org_a_successor"]  # RXZ40
    cohort_8 = multi_step_chain["cohort_8"]
    cohort_9 = multi_step_chain["cohort_9"]
    cohort_10 = multi_step_chain["cohort_10"]
    trust_c = multi_step_chain["trust_c"]

    # A sibling organisation under Trust C — the user's current affiliation
    # is Trust C.
    sibling_under_trust_c = Organisation.objects.create(
        ods_code="RXZ99",
        name="Sibling Hospital under Trust C",
        trust=trust_c,
        country=multi_step_chain["country"],
        active=True,
    )

    user = _make_user(
        email="chain-inherited-c@trust-c.nhs.uk",
        employers=[sibling_under_trust_c],
    )

    # Cohort 10 (Trust C) — inherited access granted.
    assert can_view_organisation_for_period(user, org_a_successor, cohort_10) is True
    # Cohort 8 (Trust A) and cohort 9 (Trust B) — inherited access denied.
    # The membership parent does not match the user's current parent (Trust C).
    assert (
        can_view_organisation_for_period(user, org_a_predecessor, cohort_8)
        is False
    )
    assert can_view_organisation_for_period(user, org_a_current, cohort_9) is False


# ---------------------------------------------------------------------------
# Case / registration period resolution
# ---------------------------------------------------------------------------
#
# These tests verify that case and field routes derive the period from
# ``Registration.audit_period``, that a route period cannot disagree with the
# registration period, and that the view/edit decision delegates to
# ``can_view_organisation_for_period`` with the case's lead organisation.
#
# The case factory creates a Case with a Registration, a Site (lead
# organisation) and all the related audit sub-models. Passing
# ``registration__first_paediatric_assessment_date`` and
# ``registration__audit_period__cohort_number`` pins the case to a specific
# cohort; passing ``organisations__organisation`` pins the lead site.


@pytest.mark.django_db
def test_can_view_case_resolves_period_from_registration(
    reorganisation, e12_case_factory
):
    """``can_view_case_for_period`` derives the audit period from
    ``Registration.audit_period`` when no explicit period is supplied.

    A direct user at RJZ30 can view a cohort 9 case whose lead organisation
    is RJZ30, with no ``audit_period`` argument — the period is resolved
    from the registration.
    """
    org_a_current = reorganisation["org_a_current"]  # RJZ30
    cohort_9 = reorganisation["cohort_9"]

    case = e12_case_factory(
        first_name="case_period_resolve",
        organisations__organisation=org_a_current,
        registration__first_paediatric_assessment_date=date(2026, 6, 1),
        registration__audit_period__cohort_number=9,
    )

    user = _make_user(
        email="case-direct@kch.nhs.uk",
        employers=[org_a_current],
    )

    assert can_view_case_for_period(user, case) is True


@pytest.mark.django_db
def test_can_view_case_accepts_matching_route_period(reorganisation, e12_case_factory):
    """A route period matching ``Registration.audit_period`` is accepted."""
    org_a_current = reorganisation["org_a_current"]  # RJZ30
    cohort_9 = reorganisation["cohort_9"]

    case = e12_case_factory(
        first_name="case_matching_period",
        organisations__organisation=org_a_current,
        registration__first_paediatric_assessment_date=date(2026, 6, 1),
        registration__audit_period__cohort_number=9,
    )

    user = _make_user(
        email="case-matching@kch.nhs.uk",
        employers=[org_a_current],
    )

    assert can_view_case_for_period(user, case, audit_period=cohort_9) is True


@pytest.mark.django_db
def test_can_view_case_rejects_mismatched_route_period(reorganisation, e12_case_factory):
    """A route period that does not match ``Registration.audit_period`` raises
    ``CasePeriodMismatch``.

    This protects against URL tampering — constructing a period-aware case
    URL with a period that does not match the case's actual registration
    period.
    """
    org_a_current = reorganisation["org_a_current"]  # RJZ30
    cohort_8 = reorganisation["cohort_8"]

    # Cohort 9 case.
    case = e12_case_factory(
        first_name="case_mismatch",
        organisations__organisation=org_a_current,
        registration__first_paediatric_assessment_date=date(2026, 6, 1),
        registration__audit_period__cohort_number=9,
    )

    user = _make_user(
        email="case-mismatch@kch.nhs.uk",
        employers=[org_a_current],
    )

    # Passing cohort 8 as the route period for a cohort 9 case must raise.
    with pytest.raises(CasePeriodMismatch):
        can_view_case_for_period(user, case, audit_period=cohort_8)


@pytest.mark.django_db
def test_can_view_case_direct_user_across_ods_code_change(
    reorganisation, e12_case_factory
):
    """A direct user at RJZ30 can view a cohort 8 case whose lead organisation
    is RYQ30 (the predecessor ODS code), via the shared identity chain.

    This is the case-level equivalent of direct organisation access across
    an ODS code change.
    """
    org_a_current = reorganisation["org_a_current"]  # RJZ30
    org_a_predecessor = reorganisation["org_a_predecessor"]  # RYQ30
    cohort_8 = reorganisation["cohort_8"]

    case = e12_case_factory(
        first_name="case_cross_ods",
        organisations__organisation=org_a_predecessor,
        registration__first_paediatric_assessment_date=date(2025, 6, 1),
        registration__audit_period__cohort_number=8,
    )

    user = _make_user(
        email="case-cross-ods@kch.nhs.uk",
        employers=[org_a_current],
    )

    assert can_view_case_for_period(user, case) is True


@pytest.mark.django_db
def test_can_view_case_inherited_trust_b_denied_for_cohort_8(
    reorganisation, e12_case_factory
):
    """An inherited Trust B user cannot view a cohort 8 case whose lead
    organisation is RYQ30 (Trust A period), even though the same user can
    view cohort 9 cases under Trust B.
    """
    org_a_predecessor = reorganisation["org_a_predecessor"]  # RYQ30
    org_a_current = reorganisation["org_a_current"]  # RJZ30
    cohort_8 = reorganisation["cohort_8"]
    cohort_9 = reorganisation["cohort_9"]
    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")

    user = _make_user(
        email="case-inherited-b@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    # Cohort 8 case under Trust A — denied.
    case_8 = e12_case_factory(
        first_name="case_cohort_8",
        organisations__organisation=org_a_predecessor,
        registration__first_paediatric_assessment_date=date(2025, 6, 1),
        registration__audit_period__cohort_number=8,
    )
    assert can_view_case_for_period(user, case_8) is False

    # Cohort 9 case under Trust B — allowed.
    case_9 = e12_case_factory(
        first_name="case_cohort_9",
        organisations__organisation=org_a_current,
        registration__first_paediatric_assessment_date=date(2026, 6, 1),
        registration__audit_period__cohort_number=9,
    )
    assert can_view_case_for_period(user, case_9) is True


@pytest.mark.django_db
def test_can_view_case_rcpch_user(reorganisation, e12_case_factory):
    """An RCPCH user can view any case."""
    org_a_predecessor = reorganisation["org_a_predecessor"]  # RYQ30

    case = e12_case_factory(
        first_name="case_rcpch",
        organisations__organisation=org_a_predecessor,
        registration__first_paediatric_assessment_date=date(2025, 6, 1),
        registration__audit_period__cohort_number=8,
    )

    user = _make_user(
        email="case-rcpch@rcpch.ac.uk",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        employers=[],
    )

    assert can_view_case_for_period(user, case) is True


@pytest.mark.django_db
def test_can_edit_case_combines_view_permission_with_editable(
    reorganisation, e12_case_factory
):
    """``can_edit_case_for_period`` combines the period-aware view permission
    with the case's ``editable()`` check.

    A direct user at RJZ30 can edit a cohort 9 case (editable, view
    allowed). The same case locked is not editable.
    """
    org_a_current = reorganisation["org_a_current"]  # RJZ30
    cohort_9 = reorganisation["cohort_9"]

    case = e12_case_factory(
        first_name="case_editable",
        organisations__organisation=org_a_current,
        registration__first_paediatric_assessment_date=date(2026, 6, 1),
        registration__audit_period__cohort_number=9,
    )

    user = _make_user(
        email="case-edit@kch.nhs.uk",
        employers=[org_a_current],
    )

    # Cohort 9 is in the future relative to today, so the case is editable
    # (days_remaining is not yet 0). The direct user has view access, so
    # edit is allowed.
    assert can_edit_case_for_period(user, case) is True

    # Lock the case — edit is now denied even though view is allowed.
    case.locked = True
    case.save(update_fields=["locked"])
    assert can_edit_case_for_period(user, case) is False


@pytest.mark.django_db
def test_can_edit_case_denied_for_inherited_user_outside_period(
    reorganisation, e12_case_factory
):
    """An inherited Trust B user cannot edit a cohort 8 case (Trust A period),
    even if the case is editable — the view permission is denied first."""
    org_a_predecessor = reorganisation["org_a_predecessor"]  # RYQ30
    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")

    case = e12_case_factory(
        first_name="case_edit_denied",
        organisations__organisation=org_a_predecessor,
        registration__first_paediatric_assessment_date=date(2025, 6, 1),
        registration__audit_period__cohort_number=8,
    )

    user = _make_user(
        email="case-edit-denied@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    assert can_edit_case_for_period(user, case) is False


# ---------------------------------------------------------------------------
# Pre-registration rule
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_can_view_case_pre_registration_direct_user(reorganisation, e12_case_factory):
    """A direct user at the case's lead organisation can view a case that has
    no ``Registration`` yet (pre-registration).

    The period-aware rule does not apply pre-registration; the direct/current
    organisation rule is used instead.
    """
    org_a_current = reorganisation["org_a_current"]  # RJZ30

    # Create a case with no registration. The factory creates a registration
    # by default, so we pass registration=None to suppress it.
    case = e12_case_factory(
        first_name="pre_reg_direct",
        organisations__organisation=org_a_current,
        registration=None,
    )

    user = _make_user(
        email="pre-reg-direct@kch.nhs.uk",
        employers=[org_a_current],
    )

    assert can_view_case_pre_registration(user, case) is True
    # can_view_case_for_period should also delegate to the pre-registration
    # rule when the case has no registration.
    assert can_view_case_for_period(user, case) is True


@pytest.mark.django_db
def test_can_view_case_pre_registration_rcpch_user(reorganisation, e12_case_factory):
    """An RCPCH user can view a pre-registration case."""
    org_a_current = reorganisation["org_a_current"]  # RJZ30

    case = e12_case_factory(
        first_name="pre_reg_rcpch",
        organisations__organisation=org_a_current,
        registration=None,
    )

    user = _make_user(
        email="pre-reg-rcpch@rcpch.ac.uk",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
        employers=[],
    )

    assert can_view_case_pre_registration(user, case) is True


@pytest.mark.django_db
def test_can_view_case_pre_registration_inherited_user_denied(
    reorganisation, e12_case_factory
):
    """An inherited Trust B user (not employed at the case's lead organisation)
    cannot view a pre-registration case.

    Inherited Trust/LHB access does not apply pre-registration, because
    there is no period membership to resolve the parent from.
    """
    org_a_current = reorganisation["org_a_current"]  # RJZ30
    sibling_under_trust_b = Organisation.objects.get(ods_code="RJZ01")

    case = e12_case_factory(
        first_name="pre_reg_inherited",
        organisations__organisation=org_a_current,
        registration=None,
    )

    user = _make_user(
        email="pre-reg-inherited@trust-b.nhs.uk",
        employers=[sibling_under_trust_b],
    )

    assert can_view_case_pre_registration(user, case) is False
    assert can_view_case_for_period(user, case) is False


@pytest.mark.django_db
def test_can_edit_case_pre_registration_direct_user(reorganisation, e12_case_factory):
    """A direct user can edit a pre-registration case (no deadline constraint
    yet — the submission deadline is assigned from the audit period, which
    has not been set)."""
    org_a_current = reorganisation["org_a_current"]  # RJZ30

    case = e12_case_factory(
        first_name="pre_reg_edit",
        organisations__organisation=org_a_current,
        registration=None,
    )

    user = _make_user(
        email="pre-reg-edit@kch.nhs.uk",
        employers=[org_a_current],
    )

    assert can_edit_case_pre_registration(user, case) is True
    # can_edit_case_for_period delegates to the pre-registration rule.
    assert can_edit_case_for_period(user, case) is True

    # Lock the case — edit is now denied.
    case.locked = True
    case.save(update_fields=["locked"])
    assert can_edit_case_pre_registration(user, case) is False
