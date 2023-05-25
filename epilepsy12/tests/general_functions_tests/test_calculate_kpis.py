"""
Tests the calculate_kpis function

Tests
- [ ] return None if child not registered in audit (registration.registration_date is None, or registration_eligibility_criteria_met is None or False, Site.site_is_primary_centre_of_epilepsy_care is None)

Measure 1
- [ ] Measure 1 passed (registration.kpi.paediatrician_with_expertise_in_epilepsies = 1) are seen within 2 weeks of referral 
registration_instance.assessment.epilepsy_specialist_nurse_input_date <= (registration_instance.assessment.epilepsy_specialist_nurse_referral_date + relativedelta(days=+14))
- [ ] Measure 1 failed (registration.assessment.paediatrician_with_expertise_in_epilepsies = 0) if paediatrician seen after two weeks from referral or not referred
- [ ] Measure 1 None if incomplete (assessment.consultant_paediatrician_referral_date or assessment.consultant_paediatrician_input_date or assessment.consultant_paediatrician_referral_made is None)

Measure 2
- [ ] Measure 2 passed (registration.kpi.epilepsy_specialist_nurse = 1) are seen in first year of care
registration_instance.assessment.consultant_paediatrician_input_date and registration_instance.assessment.consultant_paediatrician_referral_date are not None
- [ ] Measure 2 failed (registration.assessment.paediatrician_with_expertise_in_epilepsies = 0) if paediatrician seen after two weeks from referral or not referred
- [ ] Measure 2 None if incomplete (assessment.epilepsy_specialist_nurse_referral_made or assessment.epilepsy_specialist_nurse_input_date or assessment.epilepsy_specialist_nurse_referral_date is None)
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 



"""
