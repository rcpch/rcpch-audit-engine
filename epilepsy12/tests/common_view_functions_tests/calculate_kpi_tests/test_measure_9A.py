"""
9A `comprehensive_care_planning_agreement` - Percentage of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary.

- [x] Measure 9A passed (registration.kpi.comprehensive_care_planning_agreement == 1) if ALL OF:
    -  individualised_care_plan_in_place is True
    -  individualised_care_plan_has_parent_carer_child_agreement is True
    -  care_planning_has_been_updated_when_necessary is True
- [x] Measure 9A failed (registration.kpi.comprehensive_care_planning_agreement == 0) if ANY OF:
    -  individualised_care_plan_in_place is False
    -  individualised_care_plan_has_parent_carer_child_agreement is False
    -  care_planning_has_been_updated_when_necessary is False
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
    "individualised_care_plan_in_place, individualised_care_plan_has_parent_carer_child_agreement, has_individualised_care_plan_been_updated_in_the_last_year,expected_score",
    [
        (True, True, True, KPI_SCORE["PASS"]),
        (False, True, True, KPI_SCORE["FAIL"]),
        (True, False, True, KPI_SCORE["FAIL"]),
        (True, True, False, KPI_SCORE["FAIL"]),
        (None, True, True, KPI_SCORE["NOT_SCORED"]),
        (True, None, True, KPI_SCORE["NOT_SCORED"]),
        (True, True, None, KPI_SCORE["NOT_SCORED"]),
    ],
)
@pytest.mark.django_db
def test_measure_9A_comprehensive_care_plan(
    e12_case_factory,
    individualised_care_plan_in_place,
    individualised_care_plan_has_parent_carer_child_agreement,
    has_individualised_care_plan_been_updated_in_the_last_year,
    expected_score,
):
    """
    *PASS* ALL OF:
    -  individualised_care_plan_in_place is True
    -  individualised_care_plan_has_parent_carer_child_agreement is True
    -  care_planning_has_been_updated_when_necessary is True
    *FAIL* ANY OF:
    -  individualised_care_plan_in_place is False
    -  individualised_care_plan_has_parent_carer_child_agreement is False
    -  care_planning_has_been_updated_when_necessary is False
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_in_place=individualised_care_plan_in_place,
        registration__management__individualised_care_plan_has_parent_carer_child_agreement=individualised_care_plan_has_parent_carer_child_agreement,
        registration__management__has_individualised_care_plan_been_updated_in_the_last_year=has_individualised_care_plan_been_updated_in_the_last_year,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).comprehensive_care_planning_agreement

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"Care plan in place, updated in last year, patient+parent/carer agreement but not passing"
    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"Following attributes but not failing: {individualised_care_plan_in_place=}\n{individualised_care_plan_has_parent_carer_child_agreement=}\n{has_individualised_care_plan_been_updated_in_the_last_year=}"
    elif expected_score == KPI_SCORE["NOT_SCORED"]:
        if individualised_care_plan_in_place is None:
            assertion_message = (
                f"{individualised_care_plan_in_place=} but not `KPI_SCORE['NOT_SCORED']"
            )
        elif individualised_care_plan_has_parent_carer_child_agreement is None:
            assertion_message = f"{individualised_care_plan_has_parent_carer_child_agreement=} but not `KPI_SCORE['NOT_SCORED']"
        else:
            assertion_message = f"{has_individualised_care_plan_been_updated_in_the_last_year=} but not `KPI_SCORE['NOT_SCORED']"

    assert kpi_score == expected_score, assertion_message
