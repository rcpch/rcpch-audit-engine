"""
## Update Tests

[] Assert an Audit Centre Administrator CANNOT update users
[] Assert an audit centre clinician CANNOT update users
[] Assert an Audit Centre Lead Clinician can only update users inside own Trust
[] Assert an RCPCH Audit Lead can update users nationally, within any organisations 

[] Assert an Audit Centre Administrator can only update patients within own organisation
[] Assert an audit centre clinician  can only update patients within own organisation
[] Assert an Audit Centre Lead Clinician can only update patients within own Trust
[] Assert an RCPCH Audit Lead can update patients nationally, within any organisations

[] Assert an Audit Centre Administrator CANNOT update patient records
[] Assert an audit centre clinician can only update patient records within own organisation
[] Assert an Audit Centre Lead Clinician can only update patient records within own Trust
[] Assert an RCPCH Audit Lead can update patient records nationally, within any organisations

# First Paediatric Assessment
for field in fields: [
    'first_paediatric_assessment_in_acute_or_nonacute_setting',
    'has_number_of_episodes_since_the_first_been_documented',
    'general_examination_performed',
    'neurological_examination_performed',
    'developmental_learning_or_schooling_problems',
    'behavioural_or_emotional_problems'
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200

# Epilepsy Context
for field in fields: [
    'previous_febrile_seizure',
    'previous_acute_symptomatic_seizure',
    'is_there_a_family_history_of_epilepsy',
    'previous_neonatal_seizures',
    'were_any_of_the_epileptic_seizures_convulsive',
    'experienced_prolonged_generalized_convulsive_seizures',
    'experienced_prolonged_focal_seizures',
    'diagnosis_of_epilepsy_withdrawn',
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200

# Multiaxial Diagnosis
for field in fields: [
    'epilepsy_cause_known',
    'epilepsy_cause',
    'epilepsy_cause_categories',
    'relevant_impairments_behavioural_educational',
    'mental_health_screen',
    'mental_health_issue_identified',
    'mental_health_issue',
    'global_developmental_delay_or_learning_difficulties',
    'global_developmental_delay_or_learning_difficulties_severity',
    'autistic_spectrum_disorder',
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200

# Episode
for field in fields: [
    seizure_onset_date',
    seizure_onset_date_confidence',
    episode_definition',
    has_description_of_the_episode_or_episodes_been_gathered',
    edit_description',
    delete_description_keyword',
    epilepsy_or_nonepilepsy_status',
    epileptic_seizure_onset_type',
    focal_onset_epilepsy_checked_changed',
    epileptic_generalised_onset',
    nonepilepsy_generalised_onset',
    nonepileptic_seizure_type',
    nonepileptic_seizure_subtype',
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200

# Comorbidity
for field in fields: [
    'comorbidity_diagnosis_date',
    'comorbidity_diagnosis',
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200

# Assessment
for field in fields: [
    'consultant_paediatrician_referral_made',
    'consultant_paediatrician_referral_date',
    'consultant_paediatrician_input_date',
    'general_paediatric_centre',
    'edit_general_paediatric_centre',
    'update_general_paediatric_centre_pressed',
    'paediatric_neurologist_referral_made',
    'paediatric_neurologist_referral_date',
    'paediatric_neurologist_input_date',
    'paediatric_neurology_centre',
    'edit_paediatric_neurology_centre',
    'update_paediatric_neurology_centre_pressed',
    'childrens_epilepsy_surgical_service_referral_criteria_met',
    'childrens_epilepsy_surgical_service_referral_made',
    'childrens_epilepsy_surgical_service_referral_date',
    'childrens_epilepsy_surgical_service_input_date',
    'epilepsy_surgery_centre',
    'edit_epilepsy_surgery_centre',
    'update_epilepsy_surgery_centre_pressed',
    'delete_epilepsy_surgery_centre',
    'epilepsy_specialist_nurse_referral_made',
    'epilepsy_specialist_nurse_referral_date',
    'epilepsy_specialist_nurse_input_date',
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200

# Investigations
for field in fields: [
    'eeg_indicated',
    'eeg_request_date',
    'eeg_performed_date',
    'eeg_declined',
    'twelve_lead_ecg_status',
    'ct_head_scan_status',
    'mri_indicated',
    'mri_brain_requested_date',
    'mri_brain_reported_date',
    'mri_brain_declined',
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200

# Management
for field in fields: [
    'individualised_care_plan_in_place',
    'individualised_care_plan_date',
    'individualised_care_plan_has_parent_carer_child_agreement',
    'individualised_care_plan_includes_service_contact_details',
    'individualised_care_plan_include_first_aid',
    'individualised_care_plan_parental_prolonged_seizure_care',
    'individualised_care_plan_includes_general_participation_risk',
    'individualised_care_plan_addresses_water_safety',
    'individualised_care_plan_addresses_sudep',
    'individualised_care_plan_includes_ehcp',
    'has_individualised_care_plan_been_updated_in_the_last_year',
    'has_been_referred_for_mental_health_support',
    'has_support_for_mental_health_support',
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200

# Antiepilepsy Medicine
for field in fields: [
    'has_an_aed_been_given',
    'edit_antiepilepsy_medicine',
    'medicine_id',
    'antiepilepsy_medicine_start_date',
    'antiepilepsy_medicine_add_stop_date',
    'antiepilepsy_medicine_remove_stop_date',
    'antiepilepsy_medicine_stop_date',
    'antiepilepsy_medicine_risk_discussed',
    'is_a_pregnancy_prevention_programme_in_place',
    'has_a_valproate_annual_risk_acknowledgement_form_been_completed',
    'has_rescue_medication_been_prescribed',
]
[ ] Assert an Audit Centre Administrator can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Administrator cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Clinician can change 'rfield' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Clinician cannot vchange 'field' inside a different Trust - response.status_code == 403
[ ] Assert an Audit Centre Lead Clinician can change 'field' inside own Trust - response.status_code == 200
[ ] Assert an Audit Centre Lead Clinician cannot change 'field' inside a different Trust - response.status_code == 403
[ ] Assert an RCPCH Audit Lead can change 'field' - response.status_code == 200


"""
