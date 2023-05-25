"""
Tests for the calculate_kpi function.

Tests
- [ ] return None if child not registered in audit (registration.registration_date is None, or registration_eligibility_criteria_met is None or False, Site.site_is_primary_centre_of_epilepsy_care is None)

Measure 1
- [ ] Measure 1 passed (registration.kpi.paediatrician_with_expertise_in_epilepsies = 1) are seen within 2 weeks of referral 
registration_instance.assessment.epilepsy_specialist_nurse_input_date <= (registration_instance.assessment.epilepsy_specialist_nurse_referral_date + relativedelta(days=+14))
- [ ] Measure 1 failed (registration.assessment.paediatrician_with_expertise_in_epilepsies = 0) if paediatrician seen after two weeks from referral or not referred
- [ ] Measure 1 None if incomplete (assessment.consultant_paediatrician_referral_date or assessment.consultant_paediatrician_input_date or assessment.consultant_paediatrician_referral_made is None)

Measure 2
- [ ] Measure 2 passed (registration.kpi.epilepsy_specialist_nurse = 1) are seen in first year of care
registration_instance.assessment.epilepsy_specialist_nurse_input_date and registration_instance.assessment.epilepsy_specialist_nurse_referral_made are not None
- [ ] Measure 2 failed (registration.assessment.paediatrician_with_expertise_in_epilepsies = 0) if epilepsy_specialist_nurse not seen after referral or not referred
- [ ] Measure 2 None if incomplete (assessment.epilepsy_specialist_nurse_referral_made or assessment.epilepsy_specialist_nurse_input_date or assessment.epilepsy_specialist_nurse_referral_date is None)

Measure 3
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if age at first paediatric assessment is <= 3 and seen by neurologist or epilepsy surgery ( where age_at_first_paediatric_assessment = relativedelta(registration_instance.registration_date,registration_instance.case.date_of_birth).years)
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is on 3 or more AEMS (see lines 115-120 for query) and seen by neurologist or epilepsy surgery
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is under 4 and has myoclonic epilepsy (lines 128-133) and seen by neurologist or epilepsy surgery
- [ ] Measure 3 passed (registration.kpi.tertiary_input == 1) if child is eligible for epilepsy surgery (registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met) and seen by neurologist or epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if age at first paediatric assessment is <= 3 and not seen by neurologist or epilepsy surgery ( where age_at_first_paediatric_assessment = relativedelta(registration_instance.registration_date,registration_instance.case.date_of_birth).years)
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is on 3 or more AEMS (see lines 115-120 for query) and not seen by neurologist or epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is under 4 and has myoclonic epilepsy (lines 128-133) and not seen by neurologist or epilepsy surgery
- [ ] Measure 3 failed (registration.kpi.tertiary_input == 0) if child is eligible for epilepsy surgery (registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met) and not seen by neurologist or epilepsy surgery
- [ ] Measure 3 ineligible (registration.kpi.tertiary_input == 2) if age at first paediatric assessment is > 3 and not not on 3 or more drugs and not eligible for epilepsy surgery and not >4y with myoclonic epilepsy


"""

# Standard imports
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis

@pytest.mark.django_db
def test_calculate_kpi_function(
    e12_case_factory,
):
    """Creates an audit progress with fields filled using default values.
    """
    case = e12_case_factory()
    
    calculate_kpis(case.registration)
    
    print(case.registration.kpi)
    for attr, val in vars(case.registration.kpi).items():
        print(f"{attr} = {val}")