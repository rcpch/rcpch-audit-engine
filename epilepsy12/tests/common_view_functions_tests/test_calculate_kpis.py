"""
Tests for the calculate_kpi function.

Tests
- [x] return None if child not registered in audit (registration.registration_date is None, or registration_eligibility_criteria_met is None or False, Site.site_is_primary_centre_of_epilepsy_care is None)

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

Measure 3b
- [ ] Measure 3b passed (registration.kp.epilepsy_surgery_referral ==1 ) if met criteria for surgery and evidence of referral or being seen (line 224)

Measure 4
- [ ] Measure 4 passed (registration.kpi.ecg == 1) if ECG performed and seizure convulsive (registration_instance.epilepsycontext.were_any_of_the_epileptic_seizures_convulsive and registration_instance.investigations.twelve_lead_ecg_status)
- [ ] Measure 4 failed (registration.kpi.ecg == 0) if ECG not performed and seizure convulsive (not registration_instance.epilepsycontext.were_any_of_the_epileptic_seizures_convulsive and registration_instance.investigations.twelve_lead_ecg_status)
- [ ] Measure 4 ineligible (registration.kpi.ecg == 2) if seizure not convulsive (not registration_instance.epilepsycontext.were_any_of_the_epileptic_seizures_convulsive)

Measure 5
- [ ] Measure 5 passed (registration.kpi.mri == 1) if MRI done in 6 weeks and are NOT JME or JAE or CAE or CECTS/Rolandic or under 2 y (lines 270-324)
- [ ] Measure 5 failed (registration.kpi.mri == 0) if MRI not done in 6 weeks and are NOT JME or JAE or CAE or CECTS/Rolandic or under 2 y (lines 270-324)
- [ ] Measure 5 ineligible (registration.kpi.mri == 0) if JME or JAE or CAE or CECTS/Rolandic

Measure 6
- [ ] Measure 6 passed (registration.kpi.assessment_of_mental_health_issues == 1) if (age_at_first_paediatric_assessment >= 5) and (registration_instance.multiaxialdiagnosis.mental_health_screen)
- [ ] Measure 6 failed (registration.kpi.assessment_of_mental_health_issues == 0) if (age_at_first_paediatric_assessment >= 5) and not (registration_instance.multiaxialdiagnosis.mental_health_screen)
- [ ] Measure 6 ineligible (registration.kpi.assessment_of_mental_health_issues == 2) if (age_at_first_paediatric_assessment < 5)

Measure 7
- [ ] Measure 7 passed (registration.kpi.mri == 1) if registration_instance.multiaxialdiagnosis.mental_health_issue_identified and registration_instance.management.has_support_for_mental_health_support
- [ ] Measure 7 failed (registration.kpi.mri == 0) if not registration_instance.multiaxialdiagnosis.mental_health_issue_identified and registration_instance.management.has_support_for_mental_health_support
- [ ] Measure 7 ineligible (registration.kpi.mri == 2) if not registration_instance.multiaxialdiagnosis.mental_health_issue_identified

Measure 8
- [ ] Measure 8 passed (registration.kpi.sodium_valproate == 1) if sex == 2 and on valproate and age >= 12 (line 378) and has_a_valproate_annual_risk_acknowledgement_form_been_completed
- [ ] Measure 8 failed (registration.kpi.sodium_valproate == 1) if sex == 2 and on valproate and age >= 12 (line 378) and not has_a_valproate_annual_risk_acknowledgement_form_been_completed
- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if sex == 2 and on valproate and age >= 12 (line 378)

Measure 9
- [ ] Measure 9 passed (registration.kpi.comprehensive_care_planning_agreement) if registration_instance.management.individualised_care_plan_in_place
- [ ] Measure 9 failed (registration.kpi.comprehensive_care_planning_agreement) if not registration_instance.management.individualised_care_plan_in_place

Measure 9a
- [ ] Measure 9a (registration.kpi.patient_held_individualised_epilepsy_document == 1) if (registration_instance.management.individualised_care_plan_in_place and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9a (registration.kpi.patient_held_individualised_epilepsy_document == 0) if not (registration_instance.management.individualised_care_plan_in_place and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9a (registration.kpi.patient_held_individualised_epilepsy_document == 0) if not (registration_instance.management.individualised_care_plan_in_place) and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9a (registration.kpi.patient_held_individualised_epilepsy_document == 0) if registration_instance.management.individualised_care_plan_in_place) and not registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9a (registration.kpi.patient_held_individualised_epilepsy_document == 2) if not (registration_instance.management.individualised_care_plan_in_place)
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


@pytest.mark.django_db
def test_child_not_registered_in_audit_returns_none(e12_case_factory):
    """
    Test that calculate_kpis() returns None if child is not registered in the audit.
    """

    # creates an case with all audit values filled with default values
    case = e12_case_factory()

    # overwrite registration_date and eligibility criteria
    case.registration.registration_date = None
    case.registration.eligibility_criteria_met = None
    case.save()

    registration = Registration.objects.get(case=case)

    assert calculate_kpis(registration) is None

    # repeat with eligibility_criteria_met = False
    case.registration.registration_date = None
    case.registration.eligibility_criteria_met = False
    case.save()

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    assert calculate_kpis(registration) is None





