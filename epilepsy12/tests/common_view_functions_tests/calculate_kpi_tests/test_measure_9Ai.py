"""
9i `patient_held_individualised_epilepsy_document` - Percentage of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information.

PASS IF individualised_care_plan_in_place is True

- [x] Measure 9i passed (registration.kpi.comprehensive_care_planning_agreement == 1) if individualised_care_plan_in_place is True
- [x] Measure 9i failed (registration.kpi.comprehensive_care_planning_agreement == 1) if individualised_care_plan_in_place is False
- [x] Measure 9i not scored (registration.kpi.comprehensive_care_planning_agreement == None) if individualised_care_plan_in_place is None
"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration


@pytest.mark.parametrize(
    "individualised_care_plan_in_place, expected_score",
    [
        (True, KPI_SCORE["PASS"]),
        (False, KPI_SCORE["FAIL"]),
        (None, KPI_SCORE["NOT_SCORED"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Ai_epilepsy_document(
    e12_case_factory,
    individualised_care_plan_in_place,
    expected_score,
):
    """
    *PASS*
    1) individualised_care_plan_in_place is True
    *FAIL*
    1) individualised_care_plan_in_place == False
    *INELIGIBLE*
    1) individualised_care_plan_in_place is None
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_in_place=individualised_care_plan_in_place,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).patient_held_individualised_epilepsy_document

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"Care plan in place but not passing"
    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = (
            f"{individualised_care_plan_in_place=} but not failing measure"
        )
    elif expected_score == KPI_SCORE["NOT_SCORED"]:
        assertion_message = f"{individualised_care_plan_in_place} but not getting `KPI_SCORE['NOT_SCORED']`"

    assert kpi_score == expected_score, assertion_message
