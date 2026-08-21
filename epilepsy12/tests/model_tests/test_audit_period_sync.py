"""
Tests for the per-cohort sync, hierarchy service layer, and reconciliation.

These tests cover the PR 2 scope from ``audit-period-organisation.md``:

- command idempotency (re-running for the same period upserts the same rows);
- snapshot response parsing and ``AuditPeriodOrganisation`` upsert with
  correct hierarchy FKs;
- upsert of dissolved ``Trust`` / ``ICB`` / ``LHB`` rows from historical
  snapshots;
- ``OrganisationIdentity`` linking for ODS code succession (single and
  multi-step chains);
- candidate provenance;
- preservation of an already-reviewed historical assignment (sync does not
  overwrite approved rows);
- missing-hierarchy reporting (API 404 for a snapshot);
- approval and readiness checks;
- service results for Organisation A moving from Trust A to Trust B between
  periods;
- queries accepting an ``AuditPeriod`` instance rather than a cohort integer;
- reconciliation: hierarchy changes, registration attribution, sibling
  organisations.
"""

from datetime import date
from unittest.mock import patch, MagicMock

import pytest

from django.db.models import ProtectedError

from epilepsy12.general_functions.audit_period_hierarchy import (
    get_membership,
    get_reporting_hierarchy,
    get_organisations_for_parent,
    get_participating_organisations,
    get_expected_reporting_hierarchies,
    get_sibling_organisations,
    is_period_ready,
    period_readiness_report,
    MembershipMissing,
    MembershipUnapproved,
)
from epilepsy12.general_functions.audit_period_sync import (
    sync_audit_period,
    _sync_organisation_for_period,
    _sync_organisation_for_period_dry_run,
    _upsert_organisation_identity,
    link_organisation_identities,
)
from epilepsy12.general_functions.audit_period_reconciliation import (
    reconcile_hierarchy_changes,
    reconcile_registration_attribution,
    reconcile_sibling_organisations,
    reconcile_period,
)
from epilepsy12.models import (
    AuditPeriod,
    AuditPeriodOrganisation,
    Country,
    IntegratedCareBoard,
    LocalHealthBoard,
    NHSEnglandRegion,
    OPENUKNetwork,
    Organisation,
    OrganisationIdentity,
    Trust,
)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _make_snapshot_response(
    ods_code="RP401",
    name="GREAT ORMOND STREET HOSPITAL",
    trust_ods_code="RP4",
    trust_name="GREAT ORMOND STREET HOSPITAL NHS FOUNDATION TRUST",
    lhb_ods_code=None,
    lhb_name=None,
    icb_ods_code="QKE",
    icb_name="NHS North Central London Integrated Care Board",
    region_code="Y62",
    region_name="London",
    network_boundary_id="NTEN",
    network_name="North Thames Paediatric Epilepsy Network",
    country_boundary_id="E92000001",
    country_name="England",
    predecessor_ods_code=None,
):
    """Build a mock API snapshot response dict."""
    return {
        "ods_code": ods_code,
        "name": name,
        "trust": {
            "ods_code": trust_ods_code,
            "name": trust_name,
            "active": True,
        } if trust_ods_code else "",
        "local_health_board": {
            "ods_code": lhb_ods_code,
            "name": lhb_name,
        } if lhb_ods_code else "",
        "integrated_care_board": {
            "ods_code": icb_ods_code,
            "name": icb_name,
        } if icb_ods_code else "",
        "nhs_england_region": {
            "region_code": region_code,
            "name": region_name,
        } if region_code else "",
        "openuk_network": {
            "boundary_identifier": network_boundary_id,
            "name": network_name,
        } if network_boundary_id else "",
        "country": {
            "boundary_identifier": country_boundary_id,
            "name": country_name,
        },
        "predecessor_ods_code": predecessor_ods_code,
    }


# ---------------------------------------------------------------------------
# Hierarchy service layer — get_membership
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_membership_returns_approved_membership(
    cohort_4, england_hierarchy
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    membership = AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
        integrated_care_board=england_hierarchy["icb"],
        nhs_england_region=england_hierarchy["region"],
        openuk_network=england_hierarchy["network"],
        approved_at=date(2024, 1, 1),
    )

    result = get_membership(GOSH, cohort_4)
    assert result == membership


@pytest.mark.django_db
def test_get_membership_raises_missing(cohort_4):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    with pytest.raises(MembershipMissing):
        get_membership(GOSH, cohort_4)


@pytest.mark.django_db
def test_get_membership_raises_unapproved(cohort_4, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
        # approved_at is None
    )

    with pytest.raises(MembershipUnapproved):
        get_membership(GOSH, cohort_4)


# ---------------------------------------------------------------------------
# Hierarchy service layer — get_reporting_hierarchy
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_reporting_hierarchy_returns_dict(cohort_4, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
        integrated_care_board=england_hierarchy["icb"],
        nhs_england_region=england_hierarchy["region"],
        openuk_network=england_hierarchy["network"],
        approved_at=date(2024, 1, 1),
    )

    hierarchy = get_reporting_hierarchy(GOSH, cohort_4)
    assert hierarchy["country"] == england_hierarchy["country"]
    assert hierarchy["trust"] == england_hierarchy["trust"]
    assert hierarchy["integrated_care_board"] == england_hierarchy["icb"]
    assert hierarchy["nhs_england_region"] == england_hierarchy["region"]
    assert hierarchy["openuk_network"] == england_hierarchy["network"]
    assert hierarchy["local_health_board"] is None


# ---------------------------------------------------------------------------
# Hierarchy service layer — get_organisations_for_parent
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_organisations_for_parent_returns_siblings(
    cohort_4, england_hierarchy
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")

    # Both under the same trust for cohort 4
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=KINGS,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    orgs = get_organisations_for_parent(
        england_hierarchy["trust"], cohort_4, "trust"
    )
    org_ids = [m.organisation_id for m in orgs]
    assert GOSH.id in org_ids
    assert KINGS.id in org_ids


@pytest.mark.django_db
def test_get_organisations_for_parent_excludes_unapproved(cohort_4, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        # unapproved
    )

    orgs = get_organisations_for_parent(
        england_hierarchy["trust"], cohort_4, "trust"
    )
    assert orgs.count() == 0


# ---------------------------------------------------------------------------
# Hierarchy service layer — get_participating_organisations
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_participating_organisations_returns_approved_included(
    cohort_4, england_hierarchy
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=KINGS,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    org_ids = list(get_participating_organisations(cohort_4))
    assert GOSH.id in org_ids
    assert KINGS.id in org_ids


@pytest.mark.django_db
def test_get_participating_organisations_excludes_unapproved_and_excluded(
    cohort_4, england_hierarchy
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")

    # GOSH: approved but excluded from reporting
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
        included_in_reporting=False,
    )
    # KINGS: included but unapproved
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=KINGS,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        # unapproved
    )

    org_ids = list(get_participating_organisations(cohort_4))
    assert org_ids == []


# ---------------------------------------------------------------------------
# Hierarchy service layer — get_expected_reporting_hierarchies
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_expected_reporting_hierarchies_returns_distinct_parents(
    cohort_4, england_hierarchy
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        integrated_care_board=england_hierarchy["icb"],
        nhs_england_region=england_hierarchy["region"],
        openuk_network=england_hierarchy["network"],
        approved_at=date(2024, 1, 1),
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=KINGS,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        integrated_care_board=england_hierarchy["icb"],
        nhs_england_region=england_hierarchy["region"],
        openuk_network=england_hierarchy["network"],
        approved_at=date(2024, 1, 1),
    )

    hierarchies = get_expected_reporting_hierarchies(cohort_4)
    assert set(hierarchies.keys()) == {
        "country", "trust", "local_health_board",
        "integrated_care_board", "nhs_england_region", "openuk_network",
    }
    # Two orgs under the same trust/ICB/region/network/country — distinct = 1 each.
    assert len(hierarchies["trust"]) == 1
    assert hierarchies["trust"][0] == england_hierarchy["trust"]
    assert len(hierarchies["country"]) == 1
    assert len(hierarchies["integrated_care_board"]) == 1
    assert len(hierarchies["nhs_england_region"]) == 1
    assert len(hierarchies["openuk_network"]) == 1
    # No Welsh orgs in this period — LHB list is empty.
    assert hierarchies["local_health_board"] == []


@pytest.mark.django_db
def test_get_expected_reporting_hierarchies_excludes_unapproved(cohort_4, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        # unapproved
    )

    hierarchies = get_expected_reporting_hierarchies(cohort_4)
    assert hierarchies["trust"] == []
    assert hierarchies["country"] == []


# ---------------------------------------------------------------------------
# Hierarchy service layer — get_sibling_organisations
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_sibling_organisations(cohort_4, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=KINGS,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    siblings = get_sibling_organisations(GOSH, cohort_4)
    assert KINGS in siblings
    assert GOSH not in siblings


# ---------------------------------------------------------------------------
# Hierarchy service layer — readiness
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_is_period_ready_true_when_all_approved(cohort_4, england_hierarchy, e12_case_factory):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    e12_case_factory(
        first_name="readiness_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    assert is_period_ready(cohort_4) is True


@pytest.mark.django_db
def test_is_period_ready_false_when_unapproved(cohort_4, england_hierarchy, e12_case_factory):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    e12_case_factory(
        first_name="readiness_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        # unapproved
    )

    assert is_period_ready(cohort_4) is False


@pytest.mark.django_db
def test_is_period_ready_false_when_missing(cohort_4, e12_case_factory):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    e12_case_factory(
        first_name="readiness_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )

    # No membership row created
    assert is_period_ready(cohort_4) is False


@pytest.mark.django_db
def test_is_period_ready_false_when_unapproved_row_without_registrations(
    cohort_4, england_hierarchy
):
    """An unapproved membership row blocks readiness even when the
    organisation has no registrations in the period. The previous definition
    only checked organisations with registrations, which let unapproved
    rows for zero-registration organisations slip through. Publication and
    dashboard selectors iterate over membership rows, not registrations, so
    an unapproved row must block readiness regardless of registrations.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Unapproved membership, no registrations in the period.
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        # unapproved
    )

    assert is_period_ready(cohort_4) is False


@pytest.mark.django_db
def test_period_readiness_report_lists_unapproved_without_registrations(
    cohort_4, england_hierarchy
):
    """The readiness report should list an unapproved membership row even
    when the organisation has no registrations in the period.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        # unapproved
    )

    report = period_readiness_report(cohort_4)
    assert report["ready"] is False
    assert GOSH.id in report["unapproved_memberships"]
    assert report["missing_memberships"] == []


# ---------------------------------------------------------------------------
# Per-cohort sync — snapshot parsing and upsert
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_sync_organisation_for_period_upserts_membership(
    cohort_4, england_hierarchy
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    snapshot = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    assert result["status"] == "created"
    assert result["source"] == "snapshot"

    membership = AuditPeriodOrganisation.objects.get(
        organisation=GOSH, audit_period=cohort_4
    )
    assert membership.trust == england_hierarchy["trust"]
    assert membership.country == england_hierarchy["country"]
    assert membership.source == "snapshot"
    assert membership.approved_at is None  # candidate, not yet approved
    assert membership.trust_name_snapshot == "GREAT ORMOND STREET HOSPITAL NHS FOUNDATION TRUST"


@pytest.mark.django_db
def test_sync_does_not_overwrite_approved_rows(cohort_4, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Pre-existing approved row with a different trust
    KINGS_TRUST = Trust.objects.get(ods_code="RJZ")
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=KINGS_TRUST,
        approved_at=date(2024, 1, 1),
        approved_by=None,
        source="manual",
        notes="manually corrected",
    )

    snapshot = _make_snapshot_response()  # returns GOSH's own trust, not KINGS

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    assert result["status"] == "skipped_approved"

    membership = AuditPeriodOrganisation.objects.get(
        organisation=GOSH, audit_period=cohort_4
    )
    # The approved row is untouched
    assert membership.trust == KINGS_TRUST
    assert membership.source == "manual"


# ---------------------------------------------------------------------------
# Per-cohort sync — idempotency
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_sync_is_idempotent(cohort_4, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    snapshot = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        # First run
        _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)
        # Second run
        _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    assert AuditPeriodOrganisation.objects.filter(
        organisation=GOSH, audit_period=cohort_4
    ).count() == 1


# ---------------------------------------------------------------------------
# Per-cohort sync — missing hierarchy (API 404)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_sync_reports_api_error_non_404(cohort_4):
    """A non-404 API error from the snapshot endpoint is reported, not
    swallowed. The detail-endpoint fallback is only triggered for 404s
    (no temporal history)."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    from epilepsy12.general_functions.nhs_organisations import NHSOrganisationsAPIError

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        side_effect=NHSOrganisationsAPIError("500: Internal server error"),
    ):
        result = _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    assert result["status"] == "error"
    assert "500" in result["error"]
    assert not AuditPeriodOrganisation.objects.filter(
        organisation=GOSH, audit_period=cohort_4
    ).exists()


@pytest.mark.django_db
def test_sync_falls_back_to_detail_on_404(cohort_4, england_hierarchy):
    """When the snapshot returns 404 (no temporal history for the date),
    the sync falls back to the detail endpoint (current state)."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    from epilepsy12.general_functions.nhs_organisations import NHSOrganisationsAPIError

    detail_response = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        side_effect=NHSOrganisationsAPIError("404: No snapshot exists"),
    ), patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation",
        return_value=detail_response,
    ):
        result = _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    assert result["status"] == "created"
    assert result["source"] == "detail_fallback"

    membership = AuditPeriodOrganisation.objects.get(
        organisation=GOSH, audit_period=cohort_4
    )
    assert membership.source == "detail_fallback"


@pytest.mark.django_db
def test_sync_falls_back_to_detail_on_re_raised_404(cohort_4, england_hierarchy):
    """When the snapshot endpoint re-raises a 404 with a 'No snapshot exists'
    message (which does not contain '404'), the sync still falls back to the
    detail endpoint.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    from epilepsy12.general_functions.nhs_organisations import NHSOrganisationsAPIError

    detail_response = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        side_effect=NHSOrganisationsAPIError(
            "No snapshot exists for organisation RP401 on 2022-11-30. "
            "The organisation may not have existed on that date, or the "
            "date is before the API's temporal history installation day."
        ),
    ), patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation",
        return_value=detail_response,
    ):
        result = _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    assert result["status"] == "created"
    assert result["source"] == "detail_fallback"

    membership = AuditPeriodOrganisation.objects.get(
        organisation=GOSH, audit_period=cohort_4
    )
    assert membership.source == "detail_fallback"


@pytest.mark.django_db
def test_sync_reports_error_when_both_endpoints_fail(cohort_4):
    """If both the snapshot and the detail endpoint fail, the sync reports
    the error from the detail endpoint."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    from epilepsy12.general_functions.nhs_organisations import NHSOrganisationsAPIError

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        side_effect=NHSOrganisationsAPIError("404: No snapshot exists"),
    ), patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation",
        side_effect=NHSOrganisationsAPIError("500: Detail endpoint failed"),
    ):
        result = _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    assert result["status"] == "error"
    assert "500" in result["error"]
    assert not AuditPeriodOrganisation.objects.filter(
        organisation=GOSH, audit_period=cohort_4
    ).exists()


# ---------------------------------------------------------------------------
# Per-cohort sync — dry-run
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_dry_run_reports_create_when_no_existing_membership(
    cohort_4, england_hierarchy
):
    """The dry-run reports 'create' when no membership row exists, and writes
    nothing to the database."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    snapshot = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period_dry_run(
            GOSH, cohort_4, cohort_4.data_collection_end_date
        )

    assert result["status"] == "create"
    assert result["source"] == "snapshot"
    # Nothing written.
    assert not AuditPeriodOrganisation.objects.filter(
        organisation=GOSH, audit_period=cohort_4
    ).exists()


@pytest.mark.django_db
def test_dry_run_reports_skip_approved_when_existing_approved(
    cohort_4, england_hierarchy
):
    """The dry-run reports 'skip_approved' when an approved membership row
    already exists, and writes nothing."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    snapshot = _make_snapshot_response(
        trust_ods_code="RJZ",
        trust_name="KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST",
    )

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period_dry_run(
            GOSH, cohort_4, cohort_4.data_collection_end_date
        )

    assert result["status"] == "skip_approved"
    # The approved row is untouched.
    membership = AuditPeriodOrganisation.objects.get(
        organisation=GOSH, audit_period=cohort_4
    )
    assert membership.trust == england_hierarchy["trust"]


@pytest.mark.django_db
def test_dry_run_reports_update_with_diff_for_unapproved_row(
    cohort_4, england_hierarchy
):
    """The dry-run reports 'update' with a hierarchy diff when an unapproved
    membership row exists and the snapshot would change its trust."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS_TRUST = Trust.objects.get(ods_code="RJZ")

    # Existing unapproved row under King's trust.
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=KINGS_TRUST,
        trust_name_snapshot="KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST",
        # unapproved
    )

    # Snapshot would assign GOSH trust (the seeded GOSH trust).
    snapshot = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period_dry_run(
            GOSH, cohort_4, cohort_4.data_collection_end_date
        )

    assert result["status"] == "update"
    # The diff should mention the trust change.
    trust_changes = [c for c in result["changes"] if c.startswith("trust:")]
    assert len(trust_changes) == 1
    # Nothing written — the unapproved row still has King's trust.
    membership = AuditPeriodOrganisation.objects.get(
        organisation=GOSH, audit_period=cohort_4
    )
    assert membership.trust == KINGS_TRUST


@pytest.mark.django_db
def test_dry_run_reports_in_sync_when_nothing_would_change(
    cohort_4, england_hierarchy
):
    """The dry-run reports 'in_sync' when an unapproved membership row exists
    and the snapshot would write the same hierarchy FKs, snapshot names,
    source and included_in_reporting. The live sync would still fire
    update_or_create, but there is no meaningful change to report.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Build a snapshot whose nested hierarchy entities match the real
    # seeded GOSH hierarchy exactly, so the dry-run resolves the same FKs
    # the existing row already points at. The previous version used the
    # _make_snapshot_response defaults (hardcoded ODS codes), which did not
    # match the seeded ICB/region/network/country and so always reported
    # "update".
    trust = england_hierarchy["trust"]
    icb = england_hierarchy["icb"]
    region = england_hierarchy["region"]
    network = england_hierarchy["network"]
    country = england_hierarchy["country"]

    snapshot = _make_snapshot_response(
        trust_ods_code=trust.ods_code,
        trust_name=trust.name,
        icb_ods_code=icb.ods_code,
        icb_name=icb.name,
        region_code=region.region_code,
        region_name=region.name,
        network_boundary_id=network.boundary_identifier,
        network_name=network.name,
        country_boundary_id=country.boundary_identifier,
        country_name=country.name,
    )

    # Create an unapproved row that exactly matches what the snapshot would
    # write, including the snapshot name fields and source.
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=country,
        trust=trust,
        integrated_care_board=icb,
        nhs_england_region=region,
        openuk_network=network,
        country_name_snapshot=country.name,
        trust_name_snapshot=trust.name,
        local_health_board_name_snapshot="",
        integrated_care_board_name_snapshot=icb.name,
        nhs_england_region_name_snapshot=region.name,
        openuk_network_name_snapshot=network.name,
        source="snapshot",
        included_in_reporting=True,
        # unapproved
    )

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period_dry_run(
            GOSH, cohort_4, cohort_4.data_collection_end_date
        )

    assert result["status"] == "in_sync"
    assert result["changes"] == []


@pytest.mark.django_db
def test_dry_run_reports_snapshot_name_diff_when_fk_unchanged(
    cohort_4, england_hierarchy
):
    """The dry-run reports a snapshot-name change even when the FK is the
    same — the live sync rewrites the snapshot name from the API response,
    so a renamed trust (same ODS code, different name) is a real change.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Existing unapproved row under the seeded GOSH trust, but with a stale
    # snapshot name.
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        trust_name_snapshot="OLD TRUST NAME",
        # unapproved
    )

    # Snapshot returns the same trust ODS code but the current name.
    snapshot = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period_dry_run(
            GOSH, cohort_4, cohort_4.data_collection_end_date
        )

    assert result["status"] == "update"
    name_changes = [
        c for c in result["changes"] if c.startswith("trust_name_snapshot:")
    ]
    assert len(name_changes) == 1
    assert "OLD TRUST NAME" in name_changes[0]
    # No FK change reported.
    fk_changes = [c for c in result["changes"] if c.startswith("trust:")]
    assert fk_changes == []


@pytest.mark.django_db
def test_dry_run_reports_error_on_api_failure(cohort_4):
    """The dry-run reports 'error' when the API call fails, and writes nothing."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    from epilepsy12.general_functions.nhs_organisations import NHSOrganisationsAPIError

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        side_effect=NHSOrganisationsAPIError("500: server error"),
    ):
        result = _sync_organisation_for_period_dry_run(
            GOSH, cohort_4, cohort_4.data_collection_end_date
        )

    assert result["status"] == "error"
    assert "500" in result["error"]
    assert not AuditPeriodOrganisation.objects.filter(
        organisation=GOSH, audit_period=cohort_4
    ).exists()


@pytest.mark.django_db
def test_dry_run_reports_registration_and_case_impact_counts(
    cohort_4, england_hierarchy, e12_case_factory
):
    """The dry-run reports registration counts (in period and all periods) and
    case counts (all periods, including cases without a registration) for each
    organisation, so the audit team can see how many cases a membership change
    would touch — including cases that are attached to the organisation via
    ``Site`` but have no ``Registration`` yet.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Two registered cases in cohort 4 (the period being synced).
    e12_case_factory(
        first_name="impact_1",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )
    e12_case_factory(
        first_name="impact_2",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 7, 1),
        registration__audit_period__cohort_number=4,
    )
    # One registered case in a different cohort — should appear in the
    # all-periods registration count but not the in-period count.
    e12_case_factory(
        first_name="impact_other",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2020, 6, 1),
        registration__audit_period__cohort_number=3,
    )

    snapshot = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period_dry_run(
            GOSH, cohort_4, cohort_4.data_collection_end_date
        )

    # 2 registrations in the synced period, 3 across all periods, 3 distinct
    # cases across all periods.
    assert result["registration_count_in_period"] == 2
    assert result["registration_count_all_periods"] == 3
    assert result["case_count_all_periods"] == 3


@pytest.mark.django_db
def test_dry_run_counts_cases_without_registrations(
    cohort_4, england_hierarchy, e12_case_factory
):
    """The case count includes cases attached to the organisation via ``Site``
    that have no ``Registration``. A hierarchy change still affects which
    parent those cases group under, so they must be counted even though they
    are not yet registered for the audit.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # One registered case in cohort 4.
    e12_case_factory(
        first_name="registered",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )
    # One case attached to GOSH via Site but with no registration.
    from epilepsy12.models import Case, Site
    unregistered = Case.objects.create(
        first_name="unregistered",
        surname="test",
        date_of_birth=date(2020, 1, 1),
        nhs_number="9999999999",
        sex=1,
    )
    Site.objects.create(
        case=unregistered,
        organisation=GOSH,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
    )

    snapshot = _make_snapshot_response()

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = _sync_organisation_for_period_dry_run(
            GOSH, cohort_4, cohort_4.data_collection_end_date
        )

    assert result["registration_count_in_period"] == 1
    assert result["registration_count_all_periods"] == 1
    # Both cases counted, including the unregistered one.
    assert result["case_count_all_periods"] == 2


# ---------------------------------------------------------------------------
# Per-cohort sync — dissolved trust creation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_sync_creates_dissolved_trust_from_snapshot(cohort_4):
    """A trust that only appears in a historical snapshot (not the current
    list endpoint) is created locally with active=False so it can serve as
    an FK target for historical memberships.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    snapshot = _make_snapshot_response(
        trust_ods_code="DISS1",
        trust_name="DISSOLVED TRUST",
    )
    snapshot["trust"]["active"] = False

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    dissolved_trust = Trust.objects.get(ods_code="DISS1")
    assert dissolved_trust.name == "DISSOLVED TRUST"
    assert dissolved_trust.active is False

    membership = AuditPeriodOrganisation.objects.get(
        organisation=GOSH, audit_period=cohort_4
    )
    assert membership.trust == dissolved_trust


@pytest.mark.django_db
def test_sync_does_not_overwrite_existing_trust_current_state(cohort_4, england_hierarchy):
    """The per-cohort sync must not mutate the live ``Trust`` row's
    current-state fields (name, address, active, etc.). Those are owned by
    the current-state sync (``sync_nhs_organisations``). Historical names
    live in ``trust_name_snapshot`` on ``AuditPeriodOrganisation``.

    This guards against a regression where the snapshot upsert used
    ``update_or_create`` and would revert a renamed trust's live name to
    its historical name when syncing an old cohort.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    live_trust = england_hierarchy["trust"]
    live_name_before = live_trust.name
    live_address_before = live_trust.address_line_1
    live_active_before = live_trust.active

    # Snapshot returns the same trust ODS code but a stale (historical)
    # name and address, and active=False (as for a dissolved trust).
    snapshot = _make_snapshot_response(
        trust_ods_code=live_trust.ods_code,
        trust_name="OLD HISTORICAL TRUST NAME",
    )
    snapshot["trust"]["active"] = False
    snapshot["trust"]["address_line_1"] = "OLD ADDRESS LINE 1"

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    live_trust.refresh_from_db()
    # Live row untouched.
    assert live_trust.name == live_name_before
    assert live_trust.address_line_1 == live_address_before
    assert live_trust.active == live_active_before
    # Historical name captured on the membership row instead.
    membership = AuditPeriodOrganisation.objects.get(
        organisation=GOSH, audit_period=cohort_4
    )
    assert membership.trust_name_snapshot == "OLD HISTORICAL TRUST NAME"


# ---------------------------------------------------------------------------
# OrganisationIdentity — succession linking
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_sync_links_organisation_identity_for_succession(cohort_4):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    snapshot = _make_snapshot_response(
        predecessor_ods_code="OLD01",
    )

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        _sync_organisation_for_period(GOSH, cohort_4, cohort_4.data_collection_end_date)

    GOSH.refresh_from_db()
    assert GOSH.identity is not None

    predecessor = Organisation.objects.get(ods_code="OLD01")
    assert predecessor.identity == GOSH.identity
    assert predecessor.active is False


@pytest.mark.django_db
def test_organisation_identity_multi_step_chain():
    """Test that a multi-step succession chain (RYQ30 -> RJZ30 -> RXZ40)
    can be built by successive syncs."""
    identity = OrganisationIdentity.objects.create(name="Chain Hospital")

    org_1 = Organisation.objects.create(
        ods_code="CHAIN01", name="Chain Hospital (v1)", identity=identity
    )
    org_2 = Organisation.objects.create(
        ods_code="CHAIN02", name="Chain Hospital (v2)", identity=identity
    )
    org_3 = Organisation.objects.create(
        ods_code="CHAIN03", name="Chain Hospital (v3)", identity=identity
    )

    all_orgs = Organisation.objects.filter(identity=identity).order_by("ods_code")
    assert list(all_orgs) == [org_1, org_2, org_3]


# ---------------------------------------------------------------------------
# Identity linking (post current-state sync)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_link_organisation_identities_links_successor_to_predecessor(cohort_4):
    """After the current-state sync creates a new ODS code row,
    link_organisation_identities links it to the predecessor via
    OrganisationIdentity.

    Scenario: Organisation X01 (old code, has clinical data) was succeeded
    by X02 (new code, created by sync_nhs_organisations). The snapshot for
    X02 at a historical date walks the chain and returns predecessor_ods_code=X01.
    """
    # Old organisation (predecessor) — has clinical data, no identity
    org_old = Organisation.objects.create(
        ods_code="X01", name="Hospital X (old)", active=False
    )
    # New organisation (successor) — created by current-state sync, no identity
    org_new = Organisation.objects.create(
        ods_code="X02", name="Hospital X (new)", active=True
    )

    assert org_old.identity is None
    assert org_new.identity is None

    # Snapshot for X02 at a historical date returns predecessor_ods_code=X01
    snapshot = _make_snapshot_response(
        ods_code="X02",
        name="Hospital X (new)",
        predecessor_ods_code="X01",
    )

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = link_organisation_identities(
            reference_date=cohort_4.data_collection_end_date,
            organisations=[org_new],
        )

    assert result["linked"] == 1
    assert result["no_predecessor"] == 0
    assert result["errors"] == []

    org_new.refresh_from_db()
    org_old.refresh_from_db()
    assert org_new.identity is not None
    assert org_old.identity is not None
    assert org_new.identity == org_old.identity


@pytest.mark.django_db
def test_link_organisation_identities_skips_already_linked(cohort_4):
    """Organisations that already have an identity are skipped."""
    identity = OrganisationIdentity.objects.create(name="Already Linked")
    org = Organisation.objects.create(
        ods_code="ALREADY01", name="Already Linked Hospital",
        active=True, identity=identity
    )

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
    ) as mock_snapshot:
        result = link_organisation_identities(
            reference_date=cohort_4.data_collection_end_date,
            organisations=[org],
        )
        # Should not have called the API for an already-linked org
        mock_snapshot.assert_not_called()

    assert result["linked"] == 0
    assert result["already_linked"] == 1


@pytest.mark.django_db
def test_link_organisation_identities_no_predecessor(cohort_4):
    """An organisation with no predecessor (genuinely new hospital) is
    counted as no_predecessor, not linked."""
    org = Organisation.objects.create(
        ods_code="GENUINELY_NEW01", name="Brand New Hospital", active=True
    )

    snapshot = _make_snapshot_response(
        ods_code="GENUINELY_NEW01",
        name="Brand New Hospital",
        predecessor_ods_code=None,
    )

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot,
    ):
        result = link_organisation_identities(
            reference_date=cohort_4.data_collection_end_date,
            organisations=[org],
        )

    assert result["linked"] == 0
    assert result["no_predecessor"] == 1
    org.refresh_from_db()
    assert org.identity is None


@pytest.mark.django_db
def test_link_organisation_identities_reports_api_errors(cohort_4):
    """API errors are reported, not raised."""
    Organisation.objects.create(
        ods_code="ERROR01", name="Error Hospital", active=True
    )

    from epilepsy12.general_functions.nhs_organisations import NHSOrganisationsAPIError

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        side_effect=NHSOrganisationsAPIError("404: No snapshot exists"),
    ):
        result = link_organisation_identities(
            reference_date=cohort_4.data_collection_end_date,
            organisations=Organisation.objects.filter(ods_code="ERROR01"),
        )

    assert result["linked"] == 0
    assert result["no_predecessor"] == 0
    assert len(result["errors"]) == 1
    assert result["errors"][0][0] == "ERROR01"
    assert "404" in result["errors"][0][1]


@pytest.mark.django_db
def test_link_organisation_identities_skips_inactive_organisations(cohort_4):
    """Inactive organisations are not processed — they are likely
    predecessors that have already been linked."""
    Organisation.objects.create(
        ods_code="INACTIVE01", name="Inactive Hospital", active=False
    )

    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
    ) as mock_snapshot:
        result = link_organisation_identities(
            reference_date=cohort_4.data_collection_end_date,
            organisations=[],
        )
        mock_snapshot.assert_not_called()

    assert result["linked"] == 0
    assert result["no_predecessor"] == 0
    assert result["errors"] == []


@pytest.mark.django_db
def test_link_organisation_identities_multi_step_chain(cohort_4):
    """A multi-step succession chain (X01 -> X02 -> X03) can be built
    by calling link_organisation_identities after each current-state sync.

    First call: X02 (active, no identity) links to X01 (predecessor).
    Second call: X03 (active, no identity) links to X02 (predecessor),
    which already has an identity — so X03 joins the same identity.
    """
    # Predecessor (old code, inactive, no identity yet)
    org_01 = Organisation.objects.create(
        ods_code="MULTI01", name="Multi Hospital (v1)", active=False
    )
    # Successor (new code, active, no identity)
    org_02 = Organisation.objects.create(
        ods_code="MULTI02", name="Multi Hospital (v2)", active=True
    )

    # First call: X02 links to X01
    snapshot_02 = _make_snapshot_response(
        ods_code="MULTI02", predecessor_ods_code="MULTI01"
    )
    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot_02,
    ):
        result = link_organisation_identities(
            reference_date=cohort_4.data_collection_end_date,
            organisations=[org_02],
        )

    assert result["linked"] == 1
    org_01.refresh_from_db()
    org_02.refresh_from_db()
    assert org_01.identity == org_02.identity

    # Now X03 is created (another merger)
    org_03 = Organisation.objects.create(
        ods_code="MULTI03", name="Multi Hospital (v3)", active=True
    )
    # X02 is now inactive (it was succeeded by X03)
    org_02.active = False
    org_02.save()

    # Second call: X03 links to X02 (predecessor), which already has identity
    snapshot_03 = _make_snapshot_response(
        ods_code="MULTI03", predecessor_ods_code="MULTI02"
    )
    with patch(
        "epilepsy12.general_functions.audit_period_sync.get_organisation_snapshot",
        return_value=snapshot_03,
    ):
        result = link_organisation_identities(
            reference_date=cohort_4.data_collection_end_date,
            organisations=[org_03],
        )

    assert result["linked"] == 1
    org_01.refresh_from_db()
    org_02.refresh_from_db()
    org_03.refresh_from_db()
    assert org_01.identity == org_02.identity == org_03.identity


# ---------------------------------------------------------------------------
# Reconciliation — hierarchy changes
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_reconcile_hierarchy_changes_detects_trust_move(
    cohort_4, cohort_5, england_hierarchy
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")

    # Cohort 4: GOSH under its own trust
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    # Cohort 5: GOSH under King's trust (reorganisation)
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_5, organisation=GOSH,
        country=england_hierarchy["country"], trust=KINGS.trust,
        approved_at=date(2024, 1, 1),
    )

    changes = reconcile_hierarchy_changes(cohort_5)
    assert len(changes) == 1
    assert changes[0]["ods_code"] == "RP401"
    assert changes[0]["previous_trust"] == england_hierarchy["trust"].name
    assert changes[0]["current_trust"] == KINGS.trust.name


@pytest.mark.django_db
def test_reconcile_hierarchy_changes_no_changes(cohort_4, cohort_5, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_5, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    changes = reconcile_hierarchy_changes(cohort_5)
    assert changes == []


# ---------------------------------------------------------------------------
# Reconciliation — registration attribution
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_reconcile_registration_attribution_counts_registrations(
    cohort_4, england_hierarchy, e12_case_factory
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    e12_case_factory(
        first_name="attr_test_1",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )
    e12_case_factory(
        first_name="attr_test_2",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 7, 1),
        registration__audit_period__cohort_number=4,
    )

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    report = reconcile_registration_attribution(cohort_4)
    assert len(report["organisation_counts"]) == 1
    assert report["organisation_counts"][0]["registration_count"] == 2
    assert report["organisation_counts"][0]["membership_status"] == "approved"
    assert report["orphaned_registrations"] == []
    assert report["orphaned_memberships"] == []


@pytest.mark.django_db
def test_reconcile_registration_attribution_detects_orphaned_registrations(
    cohort_4, e12_case_factory
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    e12_case_factory(
        first_name="orphan_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )

    # No membership row created — registration is orphaned
    report = reconcile_registration_attribution(cohort_4)
    assert len(report["orphaned_registrations"]) == 1
    assert report["orphaned_registrations"][0]["ods_code"] == "RP401"


# ---------------------------------------------------------------------------
# Reconciliation — sibling organisations
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_reconcile_sibling_organisations(cohort_4, england_hierarchy):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")

    # Both under the same trust
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )
    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=KINGS,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    report = reconcile_sibling_organisations(cohort_4)
    assert len(report) == 2

    gosh_entry = next(r for r in report if r["ods_code"] == "RP401")
    assert gosh_entry["parent_type"] == "trust"
    assert gosh_entry["sibling_count"] == 1
    assert gosh_entry["siblings"][0]["ods_code"] == "RJZ01"


# ---------------------------------------------------------------------------
# Reconciliation — full report
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_reconcile_period_combines_all_reports(
    cohort_4, england_hierarchy, e12_case_factory
):
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    e12_case_factory(
        first_name="reconcile_test",
        organisations__organisation=GOSH,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__audit_period__cohort_number=4,
    )

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4, organisation=GOSH,
        country=england_hierarchy["country"], trust=england_hierarchy["trust"],
        approved_at=date(2024, 1, 1),
    )

    report = reconcile_period(cohort_4)
    assert report["period"] == 4
    assert "hierarchy_changes" in report
    assert "registration_attribution" in report
    assert "sibling_organisations" in report