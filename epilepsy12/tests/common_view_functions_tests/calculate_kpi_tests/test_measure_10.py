"""
9iii `school_individual_healthcare_plan` - Percentage of children and young people with epilepsy aged 5 years and above with evidence of a school individual healthcare plan by 1 year after first paediatric assessment.

Number of children and young people aged 5 years and above diagnosed with epilepsy at first year AND with evidence of EHCP

PASS:
- [ ] management.individualised_care_plan_includes_ehcp = True
FAIL:
- [ ] management.individualised_care_plan_includes_ehcp = False
INELIGIBLE:
- [ ] age_at_first_paediatric_assessment >= 5
"""
# Standard imports
from datetime import date
from dateutil.relativedelta import relativedelta
# Third party imports
import pytest

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration


@pytest.mark.parametrize(
    "age,individualised_care_plan_includes_ehcp, expected_score",
    [
        (relativedelta(years=5), True, KPI_SCORE["PASS"]),
        (relativedelta(years=5), False, KPI_SCORE["FAIL"]),
        (relativedelta(years=4, months=11), True, KPI_SCORE["NOT_APPLICABLE"]),
    ],
)
@pytest.mark.django_db
def test_measure_10_school_individual_healthcare_plan(
    e12_case_factory,
    age,
    individualised_care_plan_includes_ehcp,
    expected_score,
):
    
    REGISTRATION_DATE = date(2023,1,1)
    DATE_OF_BIRTH = REGISTRATION_DATE - age

    # create case
    case = e12_case_factory(
        date_of_birth = DATE_OF_BIRTH,
        registration__registration_date = REGISTRATION_DATE,
        registration__management__individualised_care_plan_includes_ehcp=individualised_care_plan_includes_ehcp,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # get KPI score
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).school_individual_healthcare_plan

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = f"individualised_care_plan_includes_ehcp is True but not passing"
    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"individualised_care_plan_includes_ehcp is False but not failing"
    else:
        assertion_message = f"age 4y11mo (<5yo) but not scoring as ineligible"

    assert kpi_score == expected_score, assertion_message
