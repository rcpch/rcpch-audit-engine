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
from epilepsy12.models import AuditPeriod, Organisation, Case


# Historical cohort definitions, kept in sync with migration
# 0063_seed_audit_periods.py. Registration.save() looks up the AuditPeriod
# for a given first_paediatric_assessment_date, so the test DB must contain
# these rows or every Registration ends up with audit_period=None.
_AUDIT_PERIODS = {
    4:  (date(2020, 12, 1), date(2021, 11, 30), date(2022, 11, 30), date(2023, 1, 10)),
    5:  (date(2021, 12, 1), date(2022, 11, 30), date(2023, 11, 30), date(2024, 1, 9)),
    6:  (date(2022, 12, 1), date(2023, 11, 30), date(2024, 11, 30), date(2025, 1, 14)),
    7:  (date(2023, 12, 1), date(2024, 11, 30), date(2025, 11, 30), date(2026, 1, 13)),
    8:  (date(2024, 12, 1), date(2025, 11, 30), date(2026, 11, 30), date(2027, 1, 12)),
    9:  (date(2025, 12, 1), date(2026, 11, 30), date(2027, 11, 30), date(2028, 1, 11)),
}


@pytest.fixture(scope="session", autouse=True)
def seed_audit_periods_fixture(django_db_blocker):
    """Ensure AuditPeriod rows exist in the test DB so Registration.save()
    can resolve audit_period from first_paediatric_assessment_date.
    Idempotent: safe with --reuse-db."""
    with django_db_blocker.unblock():
        for cohort_number, (rec_start, rec_end, dc_end, deadline) in _AUDIT_PERIODS.items():
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
def CASE_GOSH(GOSH):
    return Case.objects.get(first_name=f"child_{GOSH.name}")


@pytest.fixture
def ADDENBROOKES():
    return Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )


@pytest.fixture
def CASE_ADDENBROOKES(ADDENBROOKES):
    return Case.objects.get(first_name=f"child_{ADDENBROOKES.name}")
