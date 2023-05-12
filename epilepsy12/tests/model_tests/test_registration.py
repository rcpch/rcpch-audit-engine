from datetime import datetime, date

from unittest.mock import patch

import pytest

from epilepsy12.models import (
    Registration,
    Case,
    AuditProgress,
    KPI,
    Site,
)


@pytest.fixture()
def example_audit_progress():
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


@pytest.fixture()
def example_lead_organisation(e12Case):
    return Site.objects.filter(
        case=e12Case,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
    ).get()


@pytest.fixture()
def example_kpi(example_lead_organisation):
    return KPI.objects.create(
        organisation=example_lead_organisation.organisation,
        parent_trust=example_lead_organisation.organisation.ParentOrganisation_OrganisationName,
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


@pytest.fixture()
def example_fresh_registration(e12Case, example_audit_progress, example_kpi):
    return Registration.objects.create(
        case=e12Case, audit_progress=example_audit_progress, kpi=example_kpi
    )


@pytest.mark.django_db
def test_registration_custom_method_audit_submission_date_calculation(
    example_fresh_registration,
):
    """
    Tests the `audit_submission_date_calculation` accurately calculates audit submission date.

    This is always the second Tuesday of January, following 1 year after the first paediatric assessment.

    If registration date + 1 year IS the 2nd Tues of Jan, the submission date is the same as registration + 1 year.
    """

    dates = [
        # (registration date, expected audit submission date)
        (date(2022, 11, 1), date(2024, 1, 9)),
        (date(2022, 12, 31), date(2024, 1, 9)),
        (date(2022, 1, 9), date(2023, 1, 10)),
        (date(2022, 1, 10), date(2023, 1, 10)),
        (date(2022, 1, 11), date(2024, 1, 9)),
    ]

    for expected_input_output in dates:
        example_fresh_registration.registration_date = expected_input_output[0]
        example_fresh_registration.save()

        assert (
            example_fresh_registration.audit_submission_date == expected_input_output[1]
        )


@pytest.mark.django_db
def test_registration_custom_method_registration_date_one_year_on(
    example_fresh_registration,
):
    """
    Tests the `registration_date_one_year_on` accurately calculates one year on (registration close date).

    This is always 1 year after `registration_date`.
    """

    expected_inputs_outputs = [
        # (registration date, expected audit close date)
        (date(2022, 11, 1), date(2023, 11, 1)),
        (date(2022, 12, 31), date(2023, 12, 31)),
        (date(2022, 1, 9), date(2023, 1, 9)),
        (date(2022, 1, 10), date(2023, 1, 10)),
        (date(2022, 1, 11), date(2023, 1, 11)),
    ]

    for expected_input_output in expected_inputs_outputs:
        example_fresh_registration.registration_date = expected_input_output[0]
        example_fresh_registration.save()

        assert (
            example_fresh_registration.registration_close_date
            == expected_input_output[1]
        )

@pytest.mark.django_db
def test_registration_cohort(
    example_fresh_registration,
):
    """
    Tests cohort number is set accurately, dependent on registration_date.

    Cohorts are defined between 1st December year and 30th November in the subsequent year.
    
    Examples of cohort numbers:
        Cohort 4: 1 December 2020 - 30 November 2021
        Cohort 5: 1 December 2021 - 30 November 2022
        Cohort 6: 1 December 2022 - 30 November 2023
        Cohort 7: 1 December 2023 - 30 November 2024
        
    Dates which are too early (< 2020) should return `None`.
    """

    expected_inputs_outputs = [
        # (registration date, expected cohort)
        (date(2019, 11, 1), None),
        (date(2020, 11, 30), None),
        (date(2020, 12, 1), 4),
        (date(2021, 11, 30), 4),
        (date(2021, 12, 1), 5),
    ]

    for expected_input_output in expected_inputs_outputs:
        example_fresh_registration.registration_date = expected_input_output[0]
        example_fresh_registration.save()

        assert (
            example_fresh_registration.cohort
            == expected_input_output[1]
        )

@patch.object(Registration, 'get_current_date', return_value=date(2022, 11, 30))
@pytest.mark.django_db
def test_registration_days_remaining_before_submission(
    mocked_get_current_date,
    example_fresh_registration,
):
    """
    Tests `days_remaining_before_submission` property calculated properly.
    
    Calculated as submission date - current date, return number of days left days as an int.
    
    Test patches the example Registration instance's `.get_current_date`'s return value to always return 30 Nov 2022.
    
    NOTE: if `audit_submission_date` is before today, returns 0.
    """ 
      
    expected_inputs_outputs = [
        # (submission date, expected number of days left)
        (date(2022, 11, 30), 0),
        (date(2023, 11, 30), 365),
        (date(2024, 11, 30), 731),
        (date(2025, 11, 30), 1096),
    ]
    

    for expected_input_output in expected_inputs_outputs:
        example_fresh_registration.audit_submission_date = expected_input_output[0]
        example_fresh_registration.save()

        assert (
            example_fresh_registration.days_remaining_before_submission
            == expected_input_output[1]
        )

   