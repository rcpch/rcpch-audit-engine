"""
Tests for the ``AuditPeriodOrganisation`` and ``OrganisationIdentity`` models.

These tests cover the PR 1 scope from ``audit-period-organisation.md``:

- one row per ``(audit_period, organisation)``;
- valid English Trust/ICB/region membership;
- valid Welsh LHB membership;
- invalid or incomplete parent combinations;
- ``PROTECT`` behaviour for referenced audit periods, organisations and
  hierarchy entities;
- history creation;
- coexistence of different parent assignments for the same organisation in
  concurrent periods;
- ``OrganisationIdentity`` linking multiple ``Organisation`` rows (ODS code
  succession); and
- ``OrganisationIdentity`` ``PROTECT`` behaviour when an ``Organisation`` row
  is referenced.
"""

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from epilepsy12.models import (
    AuditPeriod,
    AuditPeriodOrganisation,
    Organisation,
    OrganisationIdentity,
)


# ---------------------------------------------------------------------------
# AuditPeriodOrganisation — uniqueness
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_one_membership_per_organisation_per_audit_period(
    cohort_4, england_hierarchy
):
    """Only one ``AuditPeriodOrganisation`` row may exist for a given
    ``(audit_period, organisation)`` pair."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
        integrated_care_board=england_hierarchy["icb"],
        nhs_england_region=england_hierarchy["region"],
        openuk_network=england_hierarchy["network"],
    )

    with pytest.raises(IntegrityError):
        AuditPeriodOrganisation.objects.create(
            audit_period=cohort_4,
            organisation=GOSH,
            country=england_hierarchy["country"],
            trust=england_hierarchy["trust"],
            integrated_care_board=england_hierarchy["icb"],
            nhs_england_region=england_hierarchy["region"],
            openuk_network=england_hierarchy["network"],
        )


# ---------------------------------------------------------------------------
# AuditPeriodOrganisation — valid English membership
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_valid_english_membership(cohort_4, england_hierarchy):
    """An English organisation can have a Trust, ICB, region, network and
    country assigned, with no LHB."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    membership = AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
        integrated_care_board=england_hierarchy["icb"],
        nhs_england_region=england_hierarchy["region"],
        openuk_network=england_hierarchy["network"],
    )

    assert membership.trust == england_hierarchy["trust"]
    assert membership.integrated_care_board == england_hierarchy["icb"]
    assert membership.nhs_england_region == england_hierarchy["region"]
    assert membership.local_health_board is None
    assert membership.included_in_reporting is True


# ---------------------------------------------------------------------------
# AuditPeriodOrganisation — valid Welsh membership
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_valid_welsh_membership(cohort_4, wales_hierarchy):
    """A Welsh organisation can have an LHB, network and country assigned,
    with no Trust/ICB/region."""
    NOAHS_ARK = Organisation.objects.get(
        ods_code="7A4H1", local_health_board__ods_code="7A4"
    )

    membership = AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=NOAHS_ARK,
        country=wales_hierarchy["country"],
        local_health_board=wales_hierarchy["lhb"],
        openuk_network=wales_hierarchy["network"],
    )

    assert membership.local_health_board == wales_hierarchy["lhb"]
    assert membership.trust is None
    assert membership.integrated_care_board is None
    assert membership.nhs_england_region is None


# ---------------------------------------------------------------------------
# AuditPeriodOrganisation — country is required
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_country_is_required(cohort_4, england_hierarchy):
    """``country`` is a non-nullable FK; creating a membership without it
    must raise."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    with pytest.raises(IntegrityError):
        AuditPeriodOrganisation.objects.create(
            audit_period=cohort_4,
            organisation=GOSH,
            # country omitted
            trust=england_hierarchy["trust"],
        )


# ---------------------------------------------------------------------------
# AuditPeriodOrganisation — concurrent periods with different parents
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_concurrent_periods_hold_different_parent_assignments(
    cohort_4, cohort_5, england_hierarchy
):
    """The same organisation can have different hierarchy assignments in
    different audit periods. This is the core scenario the model exists to
    support: an organisation moves from Trust A to Trust B between cohorts.
    """
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")

    # Cohort 4: GOSH under its own trust
    membership_4 = AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
        integrated_care_board=england_hierarchy["icb"],
        nhs_england_region=england_hierarchy["region"],
        openuk_network=england_hierarchy["network"],
    )

    # Cohort 5: GOSH under King's trust (a hypothetical reorganisation)
    membership_5 = AuditPeriodOrganisation.objects.create(
        audit_period=cohort_5,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=KINGS.trust,
        integrated_care_board=KINGS.integrated_care_board,
        nhs_england_region=KINGS.nhs_england_region,
        openuk_network=KINGS.openuk_network,
    )

    assert membership_4.trust == england_hierarchy["trust"]
    assert membership_5.trust == KINGS.trust
    assert membership_4.trust != membership_5.trust


# ---------------------------------------------------------------------------
# AuditPeriodOrganisation — PROTECT behaviour
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_protect_prevents_deleting_referenced_audit_period(
    cohort_4, england_hierarchy
):
    """An ``AuditPeriod`` referenced by a membership row cannot be deleted."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
    )

    with pytest.raises(ProtectedError):
        cohort_4.delete()


@pytest.mark.django_db
def test_protect_prevents_deleting_referenced_organisation(
    cohort_4, england_hierarchy
):
    """An ``Organisation`` referenced by a membership row cannot be deleted."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
    )

    with pytest.raises(ProtectedError):
        GOSH.delete()


@pytest.mark.django_db
def test_protect_prevents_deleting_referenced_trust(
    cohort_4, england_hierarchy
):
    """A ``Trust`` referenced by a membership row cannot be deleted."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
    )

    with pytest.raises(ProtectedError):
        england_hierarchy["trust"].delete()


@pytest.mark.django_db
def test_protect_prevents_deleting_referenced_country(
    cohort_4, england_hierarchy
):
    """A ``Country`` referenced by a membership row cannot be deleted."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
    )

    with pytest.raises(ProtectedError):
        england_hierarchy["country"].delete()


# ---------------------------------------------------------------------------
# AuditPeriodOrganisation — history
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_history_created_on_membership_creation(cohort_4, england_hierarchy):
    """Creating an ``AuditPeriodOrganisation`` row creates a corresponding
    historical record (via ``simple_history``)."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    membership = AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
    )

    assert membership.history.count() == 1
    historical = membership.history.first()
    assert historical.trust == england_hierarchy["trust"]
    assert historical.included_in_reporting is True


@pytest.mark.django_db
def test_history_records_changes(cohort_4, england_hierarchy):
    """Updating an ``AuditPeriodOrganisation`` row creates a new historical
    record."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    membership = AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
    )

    membership.included_in_reporting = False
    membership.save()

    assert membership.history.count() == 2
    latest = membership.history.first()
    assert latest.included_in_reporting is False


# ---------------------------------------------------------------------------
# AuditPeriodOrganisation — approval / provenance fields
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_default_source_and_unapproved_state(cohort_4, england_hierarchy):
    """A newly created membership defaults to ``source='api_snapshot'`` and
    ``approved_at=None`` (a candidate row awaiting audit-team approval)."""
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    membership = AuditPeriodOrganisation.objects.create(
        audit_period=cohort_4,
        organisation=GOSH,
        country=england_hierarchy["country"],
        trust=england_hierarchy["trust"],
    )

    assert membership.source == "api_snapshot"
    assert membership.approved_at is None
    assert membership.approved_by is None


# ---------------------------------------------------------------------------
# OrganisationIdentity — linking multiple Organisation rows
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_identity_links_multiple_organisation_rows():
    """Multiple ``Organisation`` rows (one per ODS code) can point at the same
    ``OrganisationIdentity``, representing the same physical hospital across
    ODS code changes."""
    identity = OrganisationIdentity.objects.create(name="Test Hospital")

    org_1 = Organisation.objects.create(
        ods_code="TEST01",
        name="Test Hospital (old code)",
        identity=identity,
    )
    org_2 = Organisation.objects.create(
        ods_code="TEST02",
        name="Test Hospital (new code)",
        identity=identity,
    )

    assert org_1.identity == identity
    assert org_2.identity == identity
    assert identity.ods_codes.count() == 2
    assert set(identity.ods_codes.all()) == {org_1, org_2}


@pytest.mark.django_db
def test_identity_resolves_all_ods_codes_in_single_query():
    """The full set of ODS codes for a hospital is available in a single
    query via ``OrganisationIdentity``."""
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

    # Simulates the RYQ30 -> RJZ30 -> RXZ40 multi-step succession chain.
    all_orgs = Organisation.objects.filter(identity=identity).order_by("ods_code")
    assert list(all_orgs) == [org_1, org_2, org_3]


@pytest.mark.django_db
def test_organisation_identity_nullable():
    """``Organisation.identity`` is nullable so existing rows are not broken
    during migration before backfill."""
    org = Organisation.objects.create(
        ods_code="NULL01",
        name="No Identity Org",
    )
    assert org.identity is None


# ---------------------------------------------------------------------------
# OrganisationIdentity — PROTECT behaviour
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_identity_protect_prevents_deleting_referenced_identity():
    """An ``OrganisationIdentity`` referenced by an ``Organisation`` cannot
    be deleted (``on_delete=PROTECT`` on ``Organisation.identity``).

    The ``PROTECT`` is on the ``Organisation.identity`` FK, which means the
    *target* (the ``OrganisationIdentity``) is protected from deletion when
    an ``Organisation`` references it. It does not prevent deleting the
    ``Organisation`` itself.
    """
    identity = OrganisationIdentity.objects.create(name="Protected Hospital")
    Organisation.objects.create(
        ods_code="PROT01", name="Protected Hospital", identity=identity
    )

    with pytest.raises(ProtectedError):
        identity.delete()


@pytest.mark.django_db
def test_identity_can_be_deleted_when_no_organisations_reference_it():
    """An ``OrganisationIdentity`` with no linked ``Organisation`` rows can
    be deleted."""
    identity = OrganisationIdentity.objects.create(name="Deletable Hospital")
    identity.delete()

    assert not OrganisationIdentity.objects.filter(pk=identity.pk).exists()


# ---------------------------------------------------------------------------
# OrganisationIdentity — history
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_identity_history_created():
    """Creating an ``OrganisationIdentity`` row creates a historical record."""
    identity = OrganisationIdentity.objects.create(name="History Test Hospital")

    assert identity.history.count() == 1
    assert identity.history.first().name == "History Test Hospital"
