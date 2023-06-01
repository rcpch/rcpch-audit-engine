"""
9iii `care_planning_has_been_updated_when_necessary` - Number of children and young people diagnosed with epilepsy at first year AND with care plan which is updated where necessary

PASS:
- [ ] management.has_individualised_care_plan_been_updated_in_the_last_year = True
FAIL:
- [ ] management.has_individualised_care_plan_been_updated_in_the_last_year = False
"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration


@pytest.mark.parametrize(
    "has_individualised_care_plan_been_updated_in_the_last_year, expected_score",
    [
        (True, KPI_SCORE["PASS"]),
        (False, KPI_SCORE["FAIL"]),
    ],
)
@pytest.mark.django_db
def test_measure_9Aiii_care_plan_update(
    e12_case_factory,
    has_individualised_care_plan_been_updated_in_the_last_year,
    expected_score,
):
    """
    *PASS*
    1) registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year == True
    *FAIL*
    1) registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year == False
    """

    # create case
    case = e12_case_factory(
        registration__management__has_individualised_care_plan_been_updated_in_the_last_year=has_individualised_care_plan_been_updated_in_the_last_year,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).care_planning_has_been_updated_when_necessary

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"has_individualised_care_plan_been_updated_in_the_last_year is True in place but not passing"

    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"has_individualised_care_plan_been_updated_in_the_last_year is False NOT in place but not failing"

    assert kpi_score == expected_score, assertion_message
