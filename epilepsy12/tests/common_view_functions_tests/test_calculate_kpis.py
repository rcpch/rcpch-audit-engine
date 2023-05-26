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

Measure 9A
- [ ] Measure 9A passed (registration.kpi.comprehensive_care_planning_agreement) if registration_instance.management.individualised_care_plan_in_place
- [ ] Measure 9A failed (registration.kpi.comprehensive_care_planning_agreement) if not registration_instance.management.individualised_care_plan_in_place

Measure 9i
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 1) if (registration_instance.management.individualised_care_plan_in_place and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 0) if not (registration_instance.management.individualised_care_plan_in_place and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 0) if not (registration_instance.management.individualised_care_plan_in_place) and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 0) if registration_instance.management.individualised_care_plan_in_place) and not registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 2) if not (registration_instance.management.individualised_care_plan_in_place)

Measure 9ii
- [ ] Measure 9ii passed (registration.kpi.patient_carer_parent_agreement_to_the_care_planning == 1) if (registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement)
- [ ] Measure 9ii failed (registration.kpi.patient_carer_parent_agreement_to_the_care_planning == 0) if (Not registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement)

Measure 9iii
- [ ] Measure 9iii passed (registration.kpi.care_planning_has_been_updated_when_necessary == 1) if (registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9iii failed (registration.kpi.care_planning_has_been_updated_when_necessary == 0) if (Not registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)

Measure 9B
- [ ] Measure 9B passed (registration.kpi.comprehensive_care_planning_content == 1) if (
            registration_instance.management.has_rescue_medication_been_prescribed
            and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_include_first_aid
            and registration_instance.management.individualised_care_plan_addresses_water_safety
            and registration_instance.management.individualised_care_plan_includes_service_contact_details
            and registration_instance.management.individualised_care_plan_includes_general_participation_risk
            and registration_instance.management.individualised_care_plan_addresses_sudep
        )
- [ ] Measure 9B failed (registration.kpi.comprehensive_care_planning_content == 0) if (
            registration_instance.management.has_rescue_medication_been_prescribed
            and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_include_first_aid
            and registration_instance.management.individualised_care_plan_addresses_water_safety
            and registration_instance.management.individualised_care_plan_includes_service_contact_details
            and registration_instance.management.individualised_care_plan_includes_general_participation_risk
            and registration_instance.management.individualised_care_plan_addresses_sudep
        ) == False

Measure 9B i
- [ ] Measure 9B i passed (registration.kpi.parental_prolonged_seizures_care_plan == 1) if (
                registration_instance.management.has_rescue_medication_been_prescribed
                and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            ) is True
- [ ] Measure 9B i failed (registration.kpi.parental_prolonged_seizures_care_plan == 0) if (
                registration_instance.management.has_rescue_medication_been_prescribed
                and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            ) is False

Measure 9B ii
- [ ] Measure 9B ii passed (registration.kpi.water_safety == 1) if (registration_instance.management.individualised_care_plan_addresses_water_safety)
- [ ] Measure 9B ii failed (registration.kpi.water_safety == 0) if not (registration_instance.management.individualised_care_plan_addresses_water_safety)

Measure 9B iii
- [ ] Measure 9B iii passed (registration.kpi.first_aid == 1) if (if registration_instance.management.individualised_care_plan_include_first_aid)
- [ ] Measure 9B iii failed (registration.kpi.first_aid == 0) if not (if registration_instance.management.individualised_care_plan_include_first_aid)

Measure 9B iv
- [ ] Measure 9B iv passed (registration.kpi.general_participation_and_risk == 1) if (registration_instance.management.individualised_care_plan_includes_general_participation_risk)
- [ ] Measure 9B iv failed (registration.kpi.general_participation_and_risk == 0) if not (registration_instance.management.individualised_care_plan_includes_general_participation_risk)

Measure 9B v
- [ ] Measure 9B v passed (registration.kpi.service_contact_details == 1) if (registration_instance.management.individualised_care_plan_includes_service_contact_details)
- [ ] Measure 9B v failed (registration.kpi.service_contact_details == 0) if not (registration_instance.management.individualised_care_plan_includes_service_contact_details)

Measure 9B vi
- [ ] Measure 9B vi passed (registration.kpi.sudep == 1) if (
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_addresses_sudep
        )
- [ ] Measure 9B vi failed (registration.kpi.sudep == 0) if not(
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_addresses_sudep
        ):

Measure 10
- [ ] Measure 10 passed (registration.kpi.school_individual_healthcare_plan == 1) if (age_at_first_paediatric_assessment >= 5) and (
                registration_instance.management.individualised_care_plan_includes_ehcp
            ):
- [ ] Measure 10 failed (registration.kpi.school_individual_healthcare_plan == 0) if not (age_at_first_paediatric_assessment >= 5) and (
                registration_instance.management.individualised_care_plan_includes_ehcp
            ):
- [ ] Measure 10 ineligible (registration.kpi.school_individual_healthcare_plan == 2) if not age_at_first_paediatric_assessment < 5
            ):


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
    """Creates an audit progress with fields filled using default values."""
    case = e12_case_factory()

    calculate_kpis(case.registration)
