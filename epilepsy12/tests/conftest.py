"""conftest.py
Configures pytest fixtures for epilepsy12 app tests.
"""

# standard imports
from datetime import date

# third-party imports
from pytest_factoryboy import register
import pytest


# rcpch imports
from epilepsy12.tests.factories import (
    seed_groups_fixture,
    seed_users_fixture,
    E12AntiEpilepsyMedicineFactory,
    E12AssessmentFactory,
    E12AuditPeriodFactory,
    E12CaseFactory,
    E12ComorbidityFactory,
    E12EpilepsyContextFactory,
    E12EpisodeFactory,
    E12FirstPaediatricAssessmentFactory,
    E12ManagementFactory,
    E12MultiaxialDiagnosisFactory,
    E12RegistrationFactory,
    E12SiteFactory,
    E12SyndromeFactory,
    E12UserFactory,
)
from epilepsy12.models import (
    AuditPeriod,
    Organisation,
    OrganisationIdentity,
    Trust,
    Country,
    AuditPeriodOrganisation,
)
# Historical cohort definitions, kept in sync with migration
# 0063_seed_audit_periods.py. Registration.save() looks up the AuditPeriod
# for a given first_paediatric_assessment_date, so the test DB must contain
# these rows or every Registration ends up with audit_period=None.
from epilepsy12.constants.audit_period_dates import AUDIT_PERIODS



@pytest.fixture(scope="session", autouse=True)
def seed_audit_periods_fixture(django_db_setup,django_db_blocker):
    """Ensure AuditPeriod rows exist in the test DB so Registration.save()
    can resolve audit_period from first_paediatric_assessment_date.
    Idempotent: safe with --reuse-db."""
    with django_db_blocker.unblock():
        for cohort_number, (rec_start, rec_end, dc_end, deadline) in AUDIT_PERIODS.items():
            AuditPeriod.objects.get_or_create(
                cohort_number=cohort_number,
                defaults={
                    "recruitment_start_date": rec_start,
                    "recruitment_end_date": rec_end,
                    "data_collection_end_date": dc_end,
                    "submission_deadline": deadline,
                    "slug": f"cohort-{cohort_number}",
                    "is_visible": False,
                },
            )


# register factories to be used across test directory

# factory object becomes lowercase-underscore form of the class name
register(E12AntiEpilepsyMedicineFactory)  # => e12_anti_epilepsy_medicine_factory
register(E12AssessmentFactory)  # => e12_assessment_factory
register(E12AuditPeriodFactory)  # => e12_audit_period_factory
register(E12CaseFactory)  # => e12_case_factory
register(E12ComorbidityFactory)  # => e12_comborbidity_factory
register(E12EpilepsyContextFactory)  # => e12_epilepsy_context
register(E12EpisodeFactory)  # => e12_episode_factory
register(
    E12FirstPaediatricAssessmentFactory
)  # => e12_first_paediatric_assessment_factory
register(E12ManagementFactory)  # => e12_management_factory
register(E12MultiaxialDiagnosisFactory)  # => e12_multiaxial_diagnosis_factory
register(E12RegistrationFactory)  # => e12_registration_factory
register(E12SiteFactory)  # => e12_site_factory
register(E12SyndromeFactory)  # => e12_syndrome_factory
register(E12UserFactory)  # => e12_user_factory


@pytest.fixture
def GOSH():
    return Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )


@pytest.fixture
def ADDENBROOKES():
    return Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )


@pytest.fixture
def england_hierarchy():
    """Return a dict of English hierarchy entities from the seeded GOSH org."""
    org = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    return {
        "country": org.country,
        "trust": org.trust,
        "icb": org.integrated_care_board,
        "region": org.nhs_england_region,
        "network": org.openuk_network,
    }


@pytest.fixture
def wales_hierarchy():
    """Return a dict of Welsh hierarchy entities from the seeded Noah's Ark org."""
    org = Organisation.objects.get(
        ods_code="7A4H1", local_health_board__ods_code="7A4"
    )
    return {
        "country": org.country,
        "lhb": org.local_health_board,
        "network": org.openuk_network,
    }


@pytest.fixture
def cohort_4():
    return AuditPeriod.objects.get(cohort_number=4)


@pytest.fixture
def cohort_5():
    return AuditPeriod.objects.get(cohort_number=5)


@pytest.fixture
def cohort_8():
    return AuditPeriod.objects.get(cohort_number=8)


@pytest.fixture
def cohort_9():
    return AuditPeriod.objects.get(cohort_number=9)


# ---------------------------------------------------------------------------
# Reorganisation canary fixture
# ---------------------------------------------------------------------------
#
# The canonical canary for period-aware permission and reporting tests:
# Princess Royal University Hospital (PRUH) moved from Trust A (South London
# Healthcare NHS Trust, ODS code ``RYQ`` — dissolved in 2013) to Trust B
# (King's College Hospital NHS Foundation Trust, ODS code ``RJZ`` — the live
# parent the seeded ``RJZ30`` organisation belongs to) at the cohort 8 -> 9
# boundary, with an ODS code change at the same boundary (``RYQ30`` ->
# ``RJZ30``). Both ``Organisation`` rows share the same ``OrganisationIdentity``.
#
# Trust A and the predecessor ``RYQ30`` organisation are not seeded (the trust
# was dissolved before the seed data was collected), so this fixture creates
# them. The fixture then creates the two approved ``AuditPeriodOrganisation``
# rows that record the period-aware reporting affiliation:
#
#   cohort 8 -> RYQ30 under Trust A (RYQ)
#   cohort 9 -> RJZ30 under Trust B (RJZ)
#
# See ``documentation/docs/development/audit-period-organisation.md`` for the
# full design, including the permission model and the multi-step succession
# chain test (RYQ30 -> RJZ30 -> RXZ40).
@pytest.fixture
def reorganisation():
    """Return a dict describing the canonical reorganisation canary.

    Keys:
        trust_a:             dissolved Trust (RYQ), ``active=False``
        trust_b:             live Trust (RJZ, King's) — the seeded parent of RJZ30
        org_a_predecessor:  predecessor Organisation (RYQ30), ``active=False``
        org_a_current:      current Organisation (RJZ30, PRUH) — seeded, live
        org_a_identity:     OrganisationIdentity shared by both RYQ30 and RJZ30
        country:            England (the seeded Country for both orgs)
        cohort_8_membership: approved AuditPeriodOrganisation for cohort 8
        cohort_9_membership: approved AuditPeriodOrganisation for cohort 9
        cohort_8:           the cohort 8 AuditPeriod
        cohort_9:           the cohort 9 AuditPeriod

    The fixture is idempotent within a test run: it uses ``get_or_create`` for
    the dissolved Trust, the predecessor Organisation and the identity, and
    ``update_or_create`` for the membership rows, so re-running the fixture
    (or running it alongside another test that creates the same rows) does not
    raise ``IntegrityError``.
    """
    england = Country.objects.get(boundary_identifier="E92000001")

    # Trust A — South London Healthcare NHS Trust (RYQ), dissolved 2013.
    trust_a, _ = Trust.objects.get_or_create(
        ods_code="RYQ",
        defaults={
            "name": "SOUTH LONDON HEALTHCARE NHS TRUST",
            "town": "ORPINGTON",
            "postcode": "BR6 8ND",
            "country": "ENGLAND",
            "active": False,
        },
    )

    # Trust B — King's College Hospital NHS Foundation Trust (RJZ), the live
    # parent the seeded RJZ30 organisation already belongs to.
    trust_b = Trust.objects.get(ods_code="RJZ")

    # The shared identity for PRUH across the ODS code change.
    org_a_identity, _ = OrganisationIdentity.objects.get_or_create(
        name="PRINCESS ROYAL UNIVERSITY HOSPITAL",
    )

    # Predecessor Organisation (RYQ30) — the dissolved ODS code. Inactive.
    org_a_predecessor, _ = Organisation.objects.get_or_create(
        ods_code="RYQ30",
        defaults={
            "name": "PRINCESS ROYAL UNIVERSITY HOSPITAL (RYQ30)",
            "trust": trust_a,
            "country": england,
            "identity": org_a_identity,
            "active": False,
        },
    )
    if org_a_predecessor.identity_id != org_a_identity.id:
        org_a_predecessor.identity = org_a_identity
        org_a_predecessor.save(update_fields=["identity"])

    # Current Organisation (RJZ30) — PRUH under King's, seeded and live.
    org_a_current = Organisation.objects.get(ods_code="RJZ30")
    if org_a_current.identity_id != org_a_identity.id:
        org_a_current.identity = org_a_identity
        org_a_current.save(update_fields=["identity"])

    cohort_8 = AuditPeriod.objects.get(cohort_number=8)
    cohort_9 = AuditPeriod.objects.get(cohort_number=9)

    # Cohort 8 membership: RYQ30 under Trust A (the dissolved trust).
    cohort_8_membership, _ = AuditPeriodOrganisation.objects.update_or_create(
        audit_period=cohort_8,
        organisation=org_a_predecessor,
        defaults={
            "country": england,
            "trust": trust_a,
            "local_health_board": None,
            "integrated_care_board": None,
            "nhs_england_region": None,
            "openuk_network": None,
            "included_in_reporting": True,
            "approved_at": date(2027, 1, 1),
            "source": "manual",
            "notes": "Reorganisation canary: PRUH under Trust A (RYQ) for cohort 8.",
        },
    )

    # Cohort 9 membership: RJZ30 under Trust B (King's, the live parent).
    cohort_9_membership, _ = AuditPeriodOrganisation.objects.update_or_create(
        audit_period=cohort_9,
        organisation=org_a_current,
        defaults={
            "country": england,
            "trust": trust_b,
            "local_health_board": None,
            "integrated_care_board": org_a_current.integrated_care_board,
            "nhs_england_region": org_a_current.nhs_england_region,
            "openuk_network": org_a_current.openuk_network,
            "included_in_reporting": True,
            "approved_at": date(2028, 1, 1),
            "source": "snapshot",
            "notes": "Reorganisation canary: PRUH under Trust B (RJZ) for cohort 9.",
        },
    )

    return {
        "trust_a": trust_a,
        "trust_b": trust_b,
        "org_a_predecessor": org_a_predecessor,
        "org_a_current": org_a_current,
        "org_a_identity": org_a_identity,
        "country": england,
        "cohort_8": cohort_8,
        "cohort_9": cohort_9,
        "cohort_8_membership": cohort_8_membership,
        "cohort_9_membership": cohort_9_membership,
    }
