import pytest

from epilepsy12.tests.factories import (
    groups_cases_seeder,
    new_e12user_factory,
    new_e12case_factory,
)
from epilepsy12.models import (
    AuditProgress,
    Site,
    KPI,
    Registration,
)

"""
AVAILABLE USERS FOR TESTS
------------------------------------------
"""


@pytest.mark.django_db
@pytest.fixture()
def e12User_GOSH(new_e12user_factory):
    """
    Creates a single authenticated E12 User object instance for tests.
    """

    return new_e12user_factory(first_name="Norm", email="normal.user@test.com")


@pytest.mark.django_db
@pytest.fixture()
def e12User_GOSH_superuser(new_e12user_factory):
    """
    Creates a single authenticated SUPERUSER E12 User object instance for tests.
    """

    return new_e12user_factory(
        first_name="Zeus", email="superuser@test.com", is_superuser=True
    )


"""
------------------------------------------
"""


"""
AVAILABLE CASES FOR TESTS
------------------------------------------
"""


@pytest.mark.django_db
@pytest.fixture()
def e12Case(new_e12case_factory):
    """
    Creates a single E12 Case object instance for tests.

    Fresh, unregistered.
    """

    return new_e12case_factory()


"""
------------------------------------------
"""
"""
AVAILABLE AUDITPROGRESS FOR TESTS
------------------------------------------
"""


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


"""
------------------------------------------
"""
"""
AVAILABLE SITE FOR TESTS
------------------------------------------
"""


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


"""
------------------------------------------
"""
"""
AVAILABLE KPI FOR TESTS
------------------------------------------
"""


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


"""
------------------------------------------
"""

"""
AVAILABLE REGISTRATIONS FOR TESTS
------------------------------------------
"""


@pytest.mark.django_db
@pytest.fixture()
def e12Registration(e12Case, e12AuditProgress, e12KPI):
    """
    Creates a single E12 Registration object instance for tests.

    """

    return Registration.objects.create(
        case=e12Case, 
        audit_progress=e12AuditProgress, 
        kpi=e12KPI,
    )


"""
------------------------------------------
"""
