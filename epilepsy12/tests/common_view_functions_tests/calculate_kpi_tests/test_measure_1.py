"""
Measure 1 - paediatrician_with_expertise_in_epilepsies
- [x] Measure 1 passed (registration.kpi.paediatrician_with_expertise_in_epilepsies = 1) are seen within 2 weeks of referral 
registration_instance.assessment.epilepsy_specialist_nurse_input_date <= (registration_instance.assessment.epilepsy_specialist_nurse_referral_date + relativedelta(days=+14))
- [x] Measure 1 failed (registration.assessment.paediatrician_with_expertise_in_epilepsies = 0) if paediatrician seen after two weeks from referral or not referred
- [x] Measure 1 None if incomplete (assessment.consultant_paediatrician_referral_date or assessment.consultant_paediatrician_input_date or assessment.consultant_paediatrician_referral_made is None)

Test Measure 2 - % of children and young people with epilepsy, with input by a ‘consultant paediatrician with expertise in epilepsies’ within 2 weeks of initial referral

Number of children and young people [diagnosed with epilepsy] at first year 
AND (
    who had [input from a paediatrician with expertise in epilepsy] 
    OR 
    a [input from a paediatric neurologist] within 2 weeks of initial referral. (initial referral to mean first paediatric assessment)
    )
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

@pytest.mark.xfail
@pytest.mark.django_db
def test_measure_1_should_pass_seen_paediatrician(
    e12_case_factory,
):
    """
    *PASS*
    1)  consultant_paediatrician_referral_made = True
        consultant_paediatrician_referral_date = registration date
        consultant_paediatrician_input_date <= 14 days after referral
    """
    
    REFERRAL_DATE = date(2023, 1, 1)
    INPUT_DATE = REFERRAL_DATE + relativedelta(days=14)
    
    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__reset = True,
        registration__assessment__consultant_paediatrician_referral_made=True,
        registration__assessment__consultant_paediatrician_referral_date=REFERRAL_DATE,
        registration__assessment__consultant_paediatrician_input_date=INPUT_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert False == KPI_SCORE['PASS'], f'Patient saw a Paediatrician IN {INPUT_DATE - REFERRAL_DATE} after referral, but did not pass measure'


@pytest.mark.django_db
def test_measure_1_should_pass_seen_neurologist(
    e12_case_factory,
):
    """
    *PASS*
    2)  paediatric_neurologist_referral_made = True
        paediatric_neurologist_referral_date = registration date
        paediatric_neurologist_input_date <= 14 days after referral

    """
    
    REFERRAL_DATE = date(2023, 1, 1)
    INPUT_DATE = REFERRAL_DATE + relativedelta(days=14)
    
    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__reset = True,
        registration__assessment__paediatric_neurologist_referral_made=True,
        registration__assessment__paediatric_neurologist_referral_date=REFERRAL_DATE,
        registration__assessment__paediatric_neurologist_input_date=INPUT_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert kpi_score == KPI_SCORE['PASS'], f'Patient saw a Neurologist IN {INPUT_DATE - REFERRAL_DATE} after referral, but did not pass measure'   

@pytest.mark.xfail
@pytest.mark.django_db
def test_measure_1_should_fail_not_seen_14_days_after_referral(
    e12_case_factory,
):
    """
    *FAIL*
    1)  consultant_paediatrician_referral_made = True
        consultant_paediatrician_referral_date = registration date
        consultant_paediatrician_input_date > 14 days after referral
        paediatric_neurologist_referral_made = True
        paediatric_neurologist_referral_date = registration date
        paediatric_neurologist_input_date > 14 days after referral

    """
    
    REFERRAL_DATE = date(2023, 1, 1)
    INPUT_DATE = REFERRAL_DATE + relativedelta(days=15)
    
    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=True,
        registration__assessment__consultant_paediatrician_referral_date=REFERRAL_DATE,
        registration__assessment__consultant_paediatrician_input_date=INPUT_DATE,
        registration__assessment__paediatric_neurologist_referral_made=True,
        registration__assessment__paediatric_neurologist_referral_date=REFERRAL_DATE,
        registration__assessment__paediatric_neurologist_input_date=INPUT_DATE,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert kpi_score == KPI_SCORE['FAIL'], f'Patient did not see a Paediatrician/Neurologist within 14 days of referral (seen after {INPUT_DATE - REFERRAL_DATE}), but did not fail measure'  

@pytest.mark.xfail
@pytest.mark.django_db
def test_measure_1_should_fail_no_doctor_involved(
    e12_case_factory,
):
    """
    *FAIL*
    1)  consultant_paediatrician_referral_made = False
        paediatric_neurologist_referral_made = False
    """
    
    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=False,
        registration__assessment__paediatric_neurologist_referral_made=False,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert kpi_score == KPI_SCORE['FAIL'], f'Patient did not see a Paediatrician/Neurologist, but did not fail measure'  
