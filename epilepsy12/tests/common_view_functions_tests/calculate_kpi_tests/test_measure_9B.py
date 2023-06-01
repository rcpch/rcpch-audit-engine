"""
9iii `comprehensive_care_planning_content` - Percentage of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning.

Number of children and young people diagnosed with epilepsy at first year 
    AND evidence of written prolonged seizures plan if prescribed rescue medication 
    AND evidence of discussion regarding water safety 
    AND first aid 
    AND participation 
    and risk 
    AND service contact details 
    AND SUDEP

PASS:
- [x] ALL ABOVE TRUE
FAIL:
- [x] Any of above false
"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration


@pytest.mark.parametrize(
    "has_rescue_medication_been_prescribed,individualised_care_plan_parental_prolonged_seizure_care,individualised_care_plan_include_first_aid,individualised_care_plan_addresses_water_safety,individualised_care_plan_includes_service_contact_details,individualised_care_plan_includes_general_participation_risk,individualised_care_plan_addresses_sudep, expected_score",
    [
        (True, True, True, True, True, True, True, KPI_SCORE["PASS"]),
        (True, False, True, True, True, True, True, KPI_SCORE["FAIL"]),
        (True, True, False, True, True, True, True, KPI_SCORE["FAIL"]),
        (True, True, True, False, True, True, True, KPI_SCORE["FAIL"]),
        (True, True, True, True, False, True, True, KPI_SCORE["FAIL"]),
        (True, True, True, True, True, False, True, KPI_SCORE["FAIL"]),
        (True, True, True, True, True, True, False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9B_comprehensive_care_planning_content(
    e12_case_factory,
    has_rescue_medication_been_prescribed,
    individualised_care_plan_parental_prolonged_seizure_care,
    individualised_care_plan_include_first_aid,
    individualised_care_plan_addresses_water_safety,
    individualised_care_plan_includes_service_contact_details,
    individualised_care_plan_includes_general_participation_risk,
    individualised_care_plan_addresses_sudep,
    expected_score,
):
    """
    *PASS*
    1) ALL True
    *FAIL*
    1) ANY False
    """

    # create case
    case = e12_case_factory(
        registration__management__has_rescue_medication_been_prescribed=has_rescue_medication_been_prescribed,
        registration__management__individualised_care_plan_parental_prolonged_seizure_care=individualised_care_plan_parental_prolonged_seizure_care,
        registration__management__individualised_care_plan_include_first_aid=individualised_care_plan_include_first_aid,
        registration__management__individualised_care_plan_addresses_water_safety=individualised_care_plan_addresses_water_safety,
        registration__management__individualised_care_plan_includes_service_contact_details=individualised_care_plan_includes_service_contact_details,
        registration__management__individualised_care_plan_includes_general_participation_risk=individualised_care_plan_includes_general_participation_risk,
        registration__management__individualised_care_plan_addresses_sudep=individualised_care_plan_addresses_sudep,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).comprehensive_care_planning_content

    # get KPI incorrectly not failing
    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"has_individualised_care_plan_been_updated_in_the_last_year is True in place but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assessed_measures = [
            "has_rescue_medication_been_prescribed",
            "individualised_care_plan_parental_prolonged_seizure_care",
            "individualised_care_plan_include_first_aid",
            "individualised_care_plan_addresses_water_safety",
            "individualised_care_plan_includes_service_contact_details",
            "individualised_care_plan_includes_general_participation_risk",
            "individualised_care_plan_addresses_sudep",
        ]
        for key, val in vars(registration.management).items():
            if (key in assessed_measures) and not val:
                assertion_message = f"{key} is False but not failing"
                break

    assert None == expected_score, assertion_message
