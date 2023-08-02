"""
Measure 2 `epilepsy_specialist_nurse`
- [x] Measure 2 passed (registration.kpi.epilepsy_specialist_nurse = 1) registration_instance.assessment.epilepsy_specialist_nurse_input_date <= registration_date + 1 year
- [x] Measure 2 failed (registration.assessment.paediatrician_with_expertise_in_epilepsies = 0) if referral_made is False or input_date > registration_date + 1 year
- [x] Measure 2 not_scored if incomplete (assessment.epilepsy_specialist_nurse_referral_made or assessment.epilepsy_specialist_nurse_input_date is None) NOTE: currently form cannot complete if both date fields are filled

Test Measure 2 - % of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care

Number of children and young people [diagnosed with epilepsy]
AND
who had input by an Epilepsy Specialist Nurse by first year (registration_date + 1 year)
"""

# Standard imports
import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.models import (
    Registration,
    KPI,
)
from epilepsy12.constants import KPI_SCORE


@pytest.mark.parametrize(
    "epilepsy_specialist_nurse_referral_made,epilepsy_specialist_nurse_referral_date,epilepsy_specialist_nurse_input_date, expected_score",
    [
        (None, None, None, KPI_SCORE["NOT_SCORED"]),
        (True, None, None, KPI_SCORE["NOT_SCORED"]),
        (True, date(2023, 1, 1), None, KPI_SCORE["NOT_SCORED"]),
    ],
)
@pytest.mark.django_db
def test_measure_2_should_not_score(
    e12_case_factory,
    epilepsy_specialist_nurse_referral_made,
    epilepsy_specialist_nurse_referral_date,
    epilepsy_specialist_nurse_input_date,
    expected_score,
):
    """
    *NOT_SCORED*
    1)  ANY epilepsy_nurse field is none
    """
    case = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_made=epilepsy_specialist_nurse_referral_made,
        registration__assessment__epilepsy_specialist_nurse_referral_date=epilepsy_specialist_nurse_referral_date,
        registration__assessment__epilepsy_specialist_nurse_input_date=epilepsy_specialist_nurse_input_date,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).epilepsy_specialist_nurse

    assertion_message = "Following attributes are None but not scoring kpi as None:\n"
    if registration.assessment.epilepsy_specialist_nurse_referral_made is None:
        assertion_message += f"epilepsy_specialist_nurse_referral_made\n"
    if registration.assessment.epilepsy_specialist_nurse_referral_date is None:
        assertion_message += f"epilepsy_specialist_nurse_referral_date\n"
    if registration.assessment.epilepsy_specialist_nurse_input_date is None:
        assertion_message += f"epilepsy_specialist_nurse_input_date\n"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.django_db
def test_measure_2_should_fail_no_referral(
    e12_case_factory,
):
    """
    *FAIL*
    1)  kpi.epilepsy_specialist_nurse_referral_made = False
    """
    case = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_made=False
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).epilepsy_specialist_nurse

    assert (
        kpi_score == KPI_SCORE["FAIL"]
    ), f"{registration.assessment.epilepsy_specialist_nurse_referral_made = } but measure is not failing"


@pytest.mark.django_db
def test_measure_2_should_fail_referral_after_1_yr(
    e12_case_factory,
):
    """
    *FAIL*
    1)  input_date > registration_date + 1 year
    """
    REGISTRATION_DATE = date(2023, 1, 1)
    REFERRAL_DATE = REGISTRATION_DATE
    INPUT_DATE = REGISTRATION_DATE + relativedelta(years=1, days=1)

    case = e12_case_factory(
        registration__registration_date=REGISTRATION_DATE,
        registration__assessment__epilepsy_specialist_nurse_referral_made=True,
        registration__assessment__epilepsy_specialist_nurse_referral_date=REFERRAL_DATE,
        registration__assessment__epilepsy_specialist_nurse_input_date=INPUT_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).epilepsy_specialist_nurse

    assert (
        kpi_score == KPI_SCORE["FAIL"]
    ), f"ESN Referral made 1y1day after registration_date but measure is not failing"



@pytest.mark.django_db
def test_measure_2_should_pass_timely_input(
    e12_case_factory,
):
    """
    *PASS*
    1)  kpi.epilepsy_specialist_nurse_referral_made = True
        AND
        kpi.epilepsy_specialist_nurse_input_date <= registration.registration_date + 1 year
    """
    REGISTRATION_DATE = date(2023, 1, 1)
    PASSING_REFERRAL_DATE = REGISTRATION_DATE
    PASSING_INPUT_DATE = REGISTRATION_DATE + relativedelta(years=1)

    case = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_made=True,
        registration__registration_date=REGISTRATION_DATE,
        registration__assessment__epilepsy_specialist_nurse_referral_date=PASSING_REFERRAL_DATE,
        registration__assessment__epilepsy_specialist_nurse_input_date=PASSING_INPUT_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).epilepsy_specialist_nurse

    assert (
        kpi_score == KPI_SCORE["PASS"]
    ), f"Seen by epilepsy nurse within {PASSING_INPUT_DATE - REGISTRATION_DATE} but measure is not passing"
