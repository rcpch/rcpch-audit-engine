"""
Measure 3 `tertiary_input`
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if age at first paediatric assessment is <= 3 and seen by neurologist or epilepsy surgery ( where age_at_first_paediatric_assessment = relativedelta(registration_instance.registration_date,registration_instance.case.date_of_birth).years)
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is on 3 or more AEMS (see lines 115-120 for query) and seen by neurologist or epilepsy surgery
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is under 4 and has myoclonic epilepsy (lines 128-133) and seen by neurologist or epilepsy surgery
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is eligible for epilepsy surgery (registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met) and seen by neurologist or epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if age at first paediatric assessment is <= 3 and not seen by neurologist or epilepsy surgery ( where age_at_first_paediatric_assessment = relativedelta(registration_instance.registration_date,registration_instance.case.date_of_birth).years)
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is on 3 or more AEMS (see lines 115-120 for query) and not seen by neurologist or epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is under 4 and has myoclonic epilepsy (lines 128-133) and not seen by neurologist or epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is eligible for epilepsy surgery (registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met) and not seen by neurologist or epilepsy surgery
- [ ] Measure 3 ineligible (registration.kpi.tertiary_input == 2) if age at first paediatric assessment is > 3 and not not on 3 or more drugs and not eligible for epilepsy surgery and not >4y with myoclonic epilepsy
Measure 3b
- [ ] Measure 3b passed (registration.kp.epilepsy_surgery_referral ==1 ) if met criteria for surgery and evidence of referral or being seen (line 224)

Test Measure 3 - % of children and young people meeting defined criteria for paediatric neurology referral, with input of tertiary care and/or CESS referral within the first year of care

Numerator: "Number of children ([less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year) OR (Number of children less than 4 years old at first assessment with epilepsy AND myoclonic seizures)  OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] ) AND had [evidence of referral or involvement of a paediatric neurologist] OR [evidence of referral or involvement of CESS]"

^above in English:
    PASS IF ANY OF:
        1. (age < 3yo at first assessment) AND (seen by neurologist or epilepsy surgery)
        2. ((age < 4yo) AND (myoclonic epilepsy)) AND (seen by neurologist or epilepsy surgery)
        3. (on >= 3 AEMS) AND (seen by neurologist or epilepsy surgery)
        4. (eligible for epilepsy surgery) AND (seen by neurologist or epilepsy surgery)
    OR MORE SIMPLY:
        If *criteria met* AND *seen*
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
def test_measure_3_should_pass(
    e12_case_factory,
):
    """ (age < 3yo at first assessment) AND (seen by neurologist or epilepsy surgery)
    *PASS*
    1. 
    
    """