"""
9A `comprehensive_care_planning_agreement` - Percentage of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary.

- [x] Measure 9A passed (registration.kpi.comprehensive_care_planning_agreement == 1) if individualised_care_plan_in_place and care_planning_has_been_updated_when_necessary
- [x] Measure 9A failed (registration.kpi.comprehensive_care_planning_agreement == 0) if individualised_care_plan_in_place == False
- [x] Measure 9A failed (registration.kpi.comprehensive_care_planning_agreement == 0) if care_planning_has_been_updated_when_necessary == False


"""

# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration


@pytest.mark.parametrize(
    "individualised_care_plan_in_place, has_individualised_care_plan_been_updated_in_the_last_year,expected_score",
    [
        (True, True, KPI_SCORE["PASS"]),
        (False, True, KPI_SCORE["FAIL"]),
        (True, False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9A_comprehensive_care_plan(
    e12_case_factory,
    individualised_care_plan_in_place,
    has_individualised_care_plan_been_updated_in_the_last_year,
    expected_score,
):
    """
    *PASS*
    1) individualised_care_plan_in_place and has_individualised_care_plan_been_updated_in_the_last_year
    *FAIL*
    1) individualised_care_plan_in_place == False
    2) has_individualised_care_plan_been_updated_in_the_last_year == False
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_in_place=individualised_care_plan_in_place,
        registration__management__has_individualised_care_plan_been_updated_in_the_last_year=has_individualised_care_plan_been_updated_in_the_last_year,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(pk=registration.kpi.pk).comprehensive_care_planning_agreement

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"Care plan in place, updated in last year, but not passing"
    elif expected_score == KPI_SCORE["FAIL"]:
        if not individualised_care_plan_in_place:
            assertion_message = f"No individualised_care_plan_in_place but not failing measure"
        else:
            assertion_message = f"has_individualised_care_plan_been_updated_in_the_last_year=False but not failing measure"
        

    assert kpi_score == expected_score, assertion_message