"""
Measure 2
- [x] Measure 2 passed (registration.kpi.epilepsy_specialist_nurse = 1) are seen in first year of care
registration_instance.assessment.epilepsy_specialist_nurse_input_date and registration_instance.assessment.epilepsy_specialist_nurse_referral_made are not None
- [x] Measure 2 failed (registration.assessment.paediatrician_with_expertise_in_epilepsies = 0) if epilepsy_specialist_nurse not seen after referral or not referred
- [x] Measure 2 None if incomplete (assessment.epilepsy_specialist_nurse_referral_made or assessment.epilepsy_specialist_nurse_input_date or assessment.epilepsy_specialist_nurse_referral_date is None)

Test Measure 2 - % of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care

Number of children and young people [diagnosed with epilepsy]
AND
who had [input from or referral to an Epilepsy Specialist Nurse] by first year
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


@pytest.mark.django_db
def test_measure_2_should_not_score(
    e12_case_factory,
):
    """
    *NOT_SCORED*
    1)  kpi.epilepsy_specialist_nurse_referral_made = None
    """
    case = e12_case_factory(
            registration__assessment__reset = True
        )
    
    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).epilepsy_specialist_nurse

    assert kpi_score == KPI_SCORE['NOT_SCORED'], f'{registration.assessment.epilepsy_specialist_nurse_referral_made = } but measure isn\'t `not scoring`'

@pytest.mark.django_db
def test_measure_2_should_fail_no_referral(
    e12_case_factory,
):
    """
    *FAIL*
    1)  kpi.epilepsy_specialist_nurse_referral_made = False
    """
    case = e12_case_factory(
            registration__assessment__epilepsy_specialist_nurse_referral_made = False
        )
    
    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).epilepsy_specialist_nurse

    assert kpi_score == KPI_SCORE['FAIL'], f'{registration.assessment.epilepsy_specialist_nurse_referral_made = } but measure is not failing'

@pytest.mark.django_db
def test_measure_2_should_fail_not_seen_before_close_date(
    e12_case_factory,
):
    """
    *FAIL*
    2)  kpi.epilepsy_specialist_nurse_referral_made = True
        AND (
            kpi.epilepsy_specialist_nurse_referral_date > registration.registration_close_date
            OR
            kpi.epilepsy_specialist_nurse_input_date > registration.registration_close_date
        )
    """
    REGISTRATION_DATE = date(2023,1,1)
    AFTER_REGISTRATION_CLOSE_REFERRAL_DATE = REGISTRATION_DATE + relativedelta(years=1, days=5)
    AFTER_REGISTRATION_CLOSE_INPUT_DATE = AFTER_REGISTRATION_CLOSE_REFERRAL_DATE + relativedelta(days=5)
    
    case = e12_case_factory(
            registration__assessment__epilepsy_specialist_nurse_referral_made = True,
            registration__registration_date = REGISTRATION_DATE,
            registration__assessment__epilepsy_specialist_nurse_referral_date = AFTER_REGISTRATION_CLOSE_REFERRAL_DATE,
            registration__assessment__epilepsy_specialist_nurse_input_date = AFTER_REGISTRATION_CLOSE_INPUT_DATE
        )
    
    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).epilepsy_specialist_nurse

    assert kpi_score == KPI_SCORE['FAIL'], f'Seen after close date ({registration.registration_date =}, {registration.registration_close_date =}, {AFTER_REGISTRATION_CLOSE_REFERRAL_DATE = }, {AFTER_REGISTRATION_CLOSE_INPUT_DATE = }) but measure is not failing'

@pytest.mark.django_db
def test_measure_2_should_pass_timely_referral(
    e12_case_factory,
):
    """
    *PASS*
    1)  kpi.epilepsy_specialist_nurse_referral_made = True
        AND
        kpi.epilepsy_specialist_nurse_referral_date <= registration.registration_close_date
        AND
        kpi.epilepsy_specialist_nurse_input_date <= registration.registration_close_date
    """
    REGISTRATION_DATE = date(2023,1,1)
    PASSING_REFERRAL_DATE = REGISTRATION_DATE + relativedelta(days=5)
    PASSING_INPUT_DATE = PASSING_REFERRAL_DATE + relativedelta(days=5)
    
    case = e12_case_factory(
            registration__assessment__epilepsy_specialist_nurse_referral_made = True,
            registration__registration_date = REGISTRATION_DATE,
            registration__assessment__epilepsy_specialist_nurse_referral_date = PASSING_REFERRAL_DATE,
            registration__assessment__epilepsy_specialist_nurse_input_date = PASSING_INPUT_DATE
        )
    
    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).epilepsy_specialist_nurse

    assert kpi_score == KPI_SCORE['PASS'], f'Seen by epilepsy nurse within {PASSING_INPUT_DATE - PASSING_REFERRAL_DATE} but measure is not passing'
