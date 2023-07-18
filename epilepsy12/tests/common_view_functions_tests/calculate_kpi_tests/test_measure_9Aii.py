"""
9ii `patient_carer_parent_agreement_to_the_care_planning` - Percentage of children and young people with epilepsy after 12 months where there was evidence of agreement between the person, their family and/or carers as appropriate.

pass criteria: 
Number of children and young people diagnosed with epilepsy at first year 
    AND 
with evidence of agreement

- [x] Measure 9ii passed (registration.kpi.patient_carer_parent_agreement_to_the_care_planning == 1) if registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement == True
- [x] Measure 9ii failed (registration.kpi.patient_carer_parent_agreement_to_the_care_planning == 1) if registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement == False
"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration


@pytest.mark.parametrize(
    "individualised_care_plan_has_parent_carer_child_agreement, expected_score",
    [
        (True, KPI_SCORE["PASS"]),
        (False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Aii_carer_patient_plan(
    e12_case_factory,
    individualised_care_plan_has_parent_carer_child_agreement,
    expected_score,
):
    """
    *PASS*
    1) registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement == True
    *FAIL*
    1) registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement == False
    """

    # create case
    case = e12_case_factory(
        registration__management__individualised_care_plan_has_parent_carer_child_agreement=individualised_care_plan_has_parent_carer_child_agreement,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).patient_carer_parent_agreement_to_the_care_planning

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"individualised_care_plan_has_parent_carer_child_agreement in place but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"individualised_care_plan_has_parent_carer_child_agreement NOT in place but not failing"

    assert kpi_score == expected_score, assertion_message
