"""
Measure 7 `mental_health_support` - Number of children and young people diagnosed with epilepsy AND had a mental health issue identified AND had evidence of mental health support received

- [x] Measure 7 passed (registration.kpi.mental_health_support == 1) if registration_instance.multiaxialdiagnosis.mental_health_issue_identified and registration_instance.management.has_support_for_mental_health_support
- [x] Measure 7 failed (registration.kpi.mental_health_support == 0) if not registration_instance.multiaxialdiagnosis.mental_health_issue_identified and registration_instance.management.has_support_for_mental_health_support
- [x] Measure 7 ineligible (registration.kpi.mental_health_support == 2) if not registration_instance.multiaxialdiagnosis.mental_health_issue_identified
"""

# Standard imports
from datetime import date
import pytest
from dateutil.relativedelta import relativedelta

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.constants import KPI_SCORE
from epilepsy12.models import (
    KPI,
    Registration,
    Management,
    MultiaxialDiagnosis,
)


@pytest.mark.parametrize(
    "mental_health_issue_identified,has_support_for_mental_health_support, expected_score",
    [
        (True, True, KPI_SCORE["PASS"]),
        (True, False, KPI_SCORE["FAIL"]),
        (False, None, KPI_SCORE["NOT_APPLICABLE"]),
    ],
)
@pytest.mark.django_db
def test_measure_7_mental_health_support(
    e12_case_factory,
    mental_health_issue_identified,
    has_support_for_mental_health_support,
    expected_score,
):
    """
    *PASS*
    1) mental_health_issue_identified and has_support_for_mental_health_support
    *FAIL*
    1) mental_health_issue_identified and NOT has_support_for_mental_health_support
    *INELIGIBLE*
    1) NOT mental_health_issue_identified

    """

    # ensure child is old enough to be scored on mental health
    DATE_OF_BIRTH = date(2018, 1, 1)
    REGISTRATION_DATE = DATE_OF_BIRTH + relativedelta(years=5)

    # create case
    case = e12_case_factory(
        date_of_birth=DATE_OF_BIRTH,
        registration__registration_date=REGISTRATION_DATE,
    )

    # update multiaxial diagnosis to corresponding mental health issue identified
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
        registration=case.registration
    )
    multiaxial_diagnosis.mental_health_issue_identified = mental_health_issue_identified
    multiaxial_diagnosis.save()

    # update management to corresponding mental health support
    management = Management.objects.get(registration=case.registration)
    management.has_support_for_mental_health_support = (
        has_support_for_mental_health_support
    )
    management.save()

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).mental_health_support

    if expected_score == KPI_SCORE["PASS"]:
        assertion_message = (
            f"Mental health issue identified and given support but not passing measure"
        )
    elif expected_score == KPI_SCORE["FAIL"]:
        assertion_message = f"Mental health issue identified but NOT given support but not failing measure"
    else:
        assertion_message = (
            f"No mental health issue identified but not scoring ineligible"
        )

    assert kpi_score == expected_score, assertion_message
