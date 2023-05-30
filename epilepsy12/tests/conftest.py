"""conftest.py
Configures pytest fixtures for epilepsy12 app tests.
"""

# standard imports
from datetime import date

# third-party imports
import pytest
from pytest_factoryboy import register

# rcpch imports
from epilepsy12.tests.factories import (
    groups_cases_seeder,
    E12AntiEpilepsyMedicineFactory,
    E12AssessmentFactory,
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
    AuditProgress,
    Site,
    KPI,
    MultiaxialDiagnosis,
    Registration,
    Syndrome,
    SyndromeEntity,
    EpilepsyCauseEntity,
)
from epilepsy12.constants import (
    SYNDROMES,
    EPILEPSY_CAUSES,
    NEUROPSYCHIATRIC,
)


# register factories to be used across test directory
# factory object becomes lowercase-underscore form of the class name
register(E12AntiEpilepsyMedicineFactory)  # => e12_anti_epilepsy_medicine_factory
register(E12AssessmentFactory)  # => e12_assessment_factory
register(E12CaseFactory)  # => e12_case_factory
register(E12ComorbidityFactory)  # => e12_comborbidity_factory
register(E12EpilepsyContextFactory)  # => e12_epilepsy_context
register(E12EpisodeFactory)  # => e12_episode_factory
register(E12FirstPaediatricAssessmentFactory)  # => e12_first_paediatric_assessment_factory
register(E12ManagementFactory)  # => e12_management_factory
register(E12RegistrationFactory)  # => e12_registration_factory
register(E12SiteFactory)  # => e12_site_factory
register(E12SyndromeFactory) # => e12_syndrome_factory
register(E12UserFactory)  # => e12_user_factory
register(E12MultiaxialDiagnosisFactory)  # => e12_multiaxial_diagnosis_factory

# AVAILABLE AUDITPROGRESS FOR TESTS


@pytest.mark.django_db
@pytest.fixture()
def e12AuditProgress():
    """
    Creates a single E12 AuditProgress object instance for tests.
    """
    return AuditProgress.objects.create(
        registration_complete=False,
        first_paediatric_assessment_complete=False,
        assessment_complete=False,
        epilepsy_context_complete=False,
        multiaxial_diagnosis_complete=False,
        management_complete=False,
        investigations_complete=False,
        registration_total_expected_fields=3,
        registration_total_completed_fields=0,
        first_paediatric_assessment_total_expected_fields=0,
        first_paediatric_assessment_total_completed_fields=0,
        assessment_total_expected_fields=0,
        assessment_total_completed_fields=0,
        epilepsy_context_total_expected_fields=0,
        epilepsy_context_total_completed_fields=0,
        multiaxial_diagnosis_total_expected_fields=0,
        multiaxial_diagnosis_total_completed_fields=0,
        investigations_total_expected_fields=0,
        investigations_total_completed_fields=0,
        management_total_expected_fields=0,
        management_total_completed_fields=0,
    )


# AVAILABLE CASES FOR TESTS


@pytest.fixture
def e12Case():
    # create new e12 case (with associated site) and save to db
    return E12CaseFactory.create()


# AVAILABLE KPI FOR TESTS


@pytest.mark.django_db
@pytest.fixture()
def e12KPI(e12Site):
    """
    Creates a single E12 KPI object instance for tests.
    """

    return KPI.objects.create(
        organisation=e12Site.organisation,
        parent_trust=e12Site.organisation.ParentOrganisation_OrganisationName,
        paediatrician_with_expertise_in_epilepsies=0,
        epilepsy_specialist_nurse=0,
        tertiary_input=0,
        epilepsy_surgery_referral=0,
        ecg=0,
        mri=0,
        assessment_of_mental_health_issues=0,
        mental_health_support=0,
        sodium_valproate=0,
        comprehensive_care_planning_agreement=0,
        patient_held_individualised_epilepsy_document=0,
        patient_carer_parent_agreement_to_the_care_planning=0,
        care_planning_has_been_updated_when_necessary=0,
        comprehensive_care_planning_content=0,
        parental_prolonged_seizures_care_plan=0,
        water_safety=0,
        first_aid=0,
        general_participation_and_risk=0,
        service_contact_details=0,
        sudep=0,
        school_individual_healthcare_plan=0,
    )


# AVAILABLE REGISTRATIONS FOR TESTS


@pytest.mark.django_db
@pytest.fixture()
def e12Registration_2023():
    """
    Creates a single E12 Registration object instance for tests.
    Uses default registration_date of 2023-1-1.
    """
    return E12RegistrationFactory.create()


@pytest.mark.django_db
@pytest.fixture()
def e12Registration_2022():
    """
    Creates a single E12 Registration object instance for tests.
    Overrides default registration date to 2022-1-1
    """
    return E12RegistrationFactory.create(registration_date=date(2022, 1, 1))


# AVAILABLE MULTIAXIALDIAGNOSIS FOR TESTS


@pytest.mark.django_db
@pytest.fixture()
def e12MultiaxialDiagnosis_2022(e12Registration_2022):
    """
    Returns a single E12 Multiaxial Diagnosis object instance for tests. Attached to `e12Registration_2022` instance - automatically created when registration created.

    Episode:
        1) Default:
            - Seizure onset 7 days before registration date
            - Approximate date confidence
            - Single Episode
            - Epileptic
            - Description
            - seizure type = Focal Onset
                - Left-sided, atonic with impaired awareness and temporal EEG findings
    """
    return MultiaxialDiagnosis.objects.get(registration=e12Registration_2022)


# AVAILABLE SITES FOR TESTS


@pytest.mark.django_db
@pytest.fixture()
def e12Site(e12Case):
    """
    Creates a single E12 Site object instance for tests.
    """
    return Site.objects.filter(
        case=e12Case,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
    ).get()


# AVAILABLE SYNDROMES FOR TESTS


@pytest.mark.django_db
@pytest.fixture()
def e12Syndrome(e12MultiaxialDiagnosis):
    """
    Creates a single E12 Syndrome object instance for tests.
    Syndrome = Sturge Weber
    `syndrome_diagnosis_date` = 27 Mar 1919 (date of 'William Allen Sturge's death)
    """
    syndrome_diagnosis_date = date(1919, 3, 19)
    syndrome_name = SYNDROMES[30][1]
    syndrome = SyndromeEntity.objects.filter(syndrome_name=syndrome_name)
    return Syndrome.objects.create(
        syndrome_diagnosis_date=syndrome_diagnosis_date,
        syndrome=syndrome,
        multiaxial_diagnosis=e12MultiaxialDiagnosis,
    )


# AVAILABLE USERS FOR TESTS


@pytest.mark.django_db
@pytest.fixture()
def e12User_GOSH():
    """
    Creates a single authenticated E12 User object instance for tests.
    """
    return E12UserFactory.create()


@pytest.mark.django_db
@pytest.fixture()
def e12User_GOSH_superuser():
    """
    Creates a single authenticated SUPERUSER E12 User object instance for tests.
    """
    return E12UserFactory.create(is_superuser=True)
