"""
9i `patient_held_individualised_epilepsy_document` - Percentage of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information.

All must be true to pass:
    individualised_care_plan_in_place
    individualised_care_plan_has_parent_carer_child_agreement
    has_individualised_care_plan_been_updated_in_the_last_year

- [x] Measure 9i passed (registration.kpi.comprehensive_care_planning_agreement == 1) if all true
- [x] Measure 9i failed (registration.kpi.comprehensive_care_planning_agreement == 1) if individualised_care_plan_in_place == False and others not None
- [x] Measure 9i failed (registration.kpi.comprehensive_care_planning_agreement == 1) if individualised_care_plan_has_parent_carer_child_agreement == False and others not None
- [x] Measure 9i failed (registration.kpi.comprehensive_care_planning_agreement == 1) if has_individualised_care_plan_been_updated_in_the_last_year == False and others not None
"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration


@pytest.mark.parametrize(
    "individualised_care_plan_in_place, individualised_care_plan_has_parent_carer_child_agreement,has_individualised_care_plan_been_updated_in_the_last_year, expected_score",
    [
        (True, True, True, KPI_SCORE["PASS"]),
        (False, True, True, KPI_SCORE["FAIL"]),
        (True, False, True, KPI_SCORE["FAIL"]),
        (True, True, False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9i_epilepsy_document(
    e12_case_factory,
    individualised_care_plan_in_place,
    individualised_care_plan_has_parent_carer_child_agreement,
    has_individualised_care_plan_been_updated_in_the_last_year,
    expected_score,
):
    """
    *PASS*
    1) all true:
        individualised_care_plan_in_place
        individualised_care_plan_has_parent_carer_child_agreement
        has_individualised_care_plan_been_updated_in_the_last_year
    *FAIL*
    1) individualised_care_plan_in_place == False
    2) individualised_care_plan_has_parent_carer_child_agreement == False
    3) has_individualised_care_plan_been_updated_in_the_last_year == False
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
    ).patient_held_individualised_epilepsy_document

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"Care plan in place, with carer-child-agreement, updated in last year, but not passing"
    elif expected_score == KPI_SCORE["FAIL"]:
        if not individualised_care_plan_in_place:
            assertion_message = (
                f"No individualised_care_plan_in_place but not failing measure"
            )
        elif not has_individualised_care_plan_been_updated_in_the_last_year:
            assertion_message = f"has_individualised_care_plan_been_updated_in_the_last_year=False but not failing measure"
        else:
            assertion_message = f"individualised_care_plan_has_parent_carer_child_agreement=False but not failing measure"

    assert kpi_score == expected_score, assertion_message
