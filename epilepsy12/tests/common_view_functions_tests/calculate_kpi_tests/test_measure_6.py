"""
Measure 6 `assessment_of_mental_health_issues` - Number of children and young people over 5 years diagnosed with epilepsy AND who had documented evidence of enquiry or screening for their mental health

- [x] Measure 6 passed (registration.kpi.assessment_of_mental_health_issues == 1) if (age_at_first_paediatric_assessment >= 5) and (registration_instance.multiaxialdiagnosis.mental_health_screen)
- [x] Measure 6 failed (registration.kpi.assessment_of_mental_health_issues == 0) if (age_at_first_paediatric_assessment >= 5) and not (registration_instance.multiaxialdiagnosis.mental_health_screen)
- [x] Measure 6 ineligible (registration.kpi.assessment_of_mental_health_issues == 2) if (age_at_first_paediatric_assessment < 5)
"""

from datetime import date

# Standard imports
import pytest
from dateutil.relativedelta import relativedelta

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import KPI, Registration, MultiaxialDiagnosis


@pytest.mark.parametrize(
    "age_fpa,mental_health_screen_done, expected_score",
    [
        (relativedelta(years=5), True, KPI_SCORE["PASS"]),
        (relativedelta(years=5), False, KPI_SCORE["FAIL"]),
        (relativedelta(years=4, months=11), True, KPI_SCORE["INELIGIBLE"]),
    ],
)
@pytest.mark.django_db
def test_measure_6_screen_mental_health(
    e12_case_factory, age_fpa, mental_health_screen_done, expected_score
):
    """
    *PASS*
    1) (age_at_first_paediatric_assessment >= 5) and (registration_instance.multiaxialdiagnosis.mental_health_screen)
    *FAIL*
    1) (age_at_first_paediatric_assessment >= 5) and NOT (registration_instance.multiaxialdiagnosis.mental_health_screen)
    *INELIGIBLE*
    1) (age_at_first_paediatric_assessment < 5)
    """

    DATE_OF_BIRTH = date(2018, 1, 1)
    REGISTRATION_DATE = DATE_OF_BIRTH + age_fpa

    # create case
    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__registration_date=REGISTRATION_DATE,
    )

    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        registration=case.registration
    )
    multiaxial_diagnosis.mental_health_screen = mental_health_screen_done
    multiaxial_diagnosis.save()

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).assessment_of_mental_health_issues

    # get age for AssertionError message
    age = relativedelta(case.registration.registration_date, case.date_of_birth).years

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = (
            f"Age >= 5yo ({age}yo) with mental health screen but not passing measure"
        )
    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = (
            f"Age >= 5yo ({age}yo) with NO mental health screen but not failing measure"
        )
    else:
        assertion_message = f"Age < 5yo ({age}yo) should be ineligible for measure"

    assert kpi_score == expected_score, assertion_message
