"""
# Epilepsy12Users
    [] Assert user can change user title
    [] Assert user can change user first_name
    [] Assert user can change user surname
    [] Assert user can change user email
    [] Assert user can change user role
    [] Assert user can resend create_user email
    

# Cases
    [] Assert user can change child first_name
    [] Assert user can change child surname
    [] Assert user can change child date_of_birth
    [] Assert user can change child sex
    [] Assert user can change child postcode
    [] Assert user can change child postcode to unknown
    [] Assert user can change child postcode to address unspecified
    [] Assert user can change child postcode to no fixed abode
    [] Assert user can change child nhs_number
    [] Assert user can change child ethnicity
    [] Assert user can opt child out of Epilepsy12
    

# First Paediatric Assessment
    for field in fields: [
        'first_paediatric_assessment_in_acute_or_nonacute_setting', single_choice_multiple_toggle_button
        'has_number_of_episodes_since_the_first_been_documented',   toggle_button
        'general_examination_performed',                            toggle_button
        'neurological_examination_performed',                       toggle_button
        'developmental_learning_or_schooling_problems',             toggle_button
        'behavioural_or_emotional_problems'                         toggle_button
    ]
    [x] Assert user can change 'first_paediatric_assessment_in_acute_or_nonacute_setting' to acute (CHRONICITY[0][0]==1)
    [x] Assert user can change 'first_paediatric_assessment_in_acute_or_nonacute_setting' to non-acute (CHRONICITY[0][0]==2)
    [x] Assert user can change 'first_paediatric_assessment_in_acute_or_nonacute_setting' to don't know (CHRONICITY[0][0]==3)
    [x] Assert user can change 'has_number_of_episodes_since_the_first_been_documented' to True
    [x] Assert user can change 'has_number_of_episodes_since_the_first_been_documented' to False
    [x] Assert user can change 'general_examination_performed' to True
    [x] Assert user can change 'general_examination_performed' to False
    [x] Assert user can change 'neurological_examination_performed' to True
    [x] Assert user can change 'neurological_examination_performed' to False
    [x] Assert user can change 'developmental_learning_or_schooling_problems' to True
    [x] Assert user can change 'developmental_learning_or_schooling_problems' to False
    [x] Assert user can change 'behavioural_or_emotional_problems' to True
    [x] Assert user can change 'behavioural_or_emotional_problems' to False
    
# Epilepsy Context
    for field in fields: [
        'previous_febrile_seizure',                                 single_choice_multiple_toggle_button 
        'previous_acute_symptomatic_seizure',                       single_choice_multiple_toggle_button
        'is_there_a_family_history_of_epilepsy',                    single_choice_multiple_toggle_button
        'previous_neonatal_seizures',                               single_choice_multiple_toggle_button
        'were_any_of_the_epileptic_seizures_convulsive',            toggle_button
        'experienced_prolonged_generalized_convulsive_seizures',    single_choice_multiple_toggle_button
        'experienced_prolonged_focal_seizures',                     single_choice_multiple_toggle_button
        'diagnosis_of_epilepsy_withdrawn',                          toggle_button
    ]

    [x] Assert user can change 'previous_febrile_seizure' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [x] Assert user can change 'previous_febrile_seizure' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [x] Assert user can change 'previous_febrile_seizure' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [x] Assert user can change 'previous_acute_symptomatic_seizure' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [x] Assert user can change 'previous_acute_symptomatic_seizure' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [x] Assert user can change 'previous_acute_symptomatic_seizure' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [x] Assert user can change 'is_there_a_family_history_of_epilepsy' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [x] Assert user can change 'is_there_a_family_history_of_epilepsy' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [x] Assert user can change 'is_there_a_family_history_of_epilepsy' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [x] Assert user can change 'previous_neonatal_seizures' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [x] Assert user can change 'previous_neonatal_seizures' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [x] Assert user can change 'previous_neonatal_seizures' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [x] Assert user can change 'were_any_of_the_epileptic_seizures_convulsive' to True
    [x] Assert user can change 'were_any_of_the_epileptic_seizures_convulsive' to False
    [x] Assert user can change 'experienced_prolonged_generalized_convulsive_seizures' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [x] Assert user can change 'experienced_prolonged_generalized_convulsive_seizures' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [x] Assert user can change 'experienced_prolonged_generalized_convulsive_seizures' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [x] Assert user can change 'experienced_prolonged_focal_seizures' to Yes (OPT_OUT_UNCERTAIN[0][0] == 'Y')
    [x] Assert user can change 'experienced_prolonged_focal_seizures' to No (OPT_OUT_UNCERTAIN[1][0] == 'N')
    [x] Assert user can change 'experienced_prolonged_focal_seizures' to Uncertain (OPT_OUT_UNCERTAIN[2][0] == 'U')
    [x] Assert user can change 'diagnosis_of_epilepsy_withdrawn' to True
    [x] Assert user can change 'diagnosis_of_epilepsy_withdrawn' to False



# Multiaxial Diagnosis
    for field in fields: [
        'epilepsy_cause_known',                                         toggle_button
        'epilepsy_cause',                                               select
        'epilepsy_cause_categories',                                    multiple_choice_multiple_toggle_button
        'relevant_impairments_behavioural_educational',                 toggle_button
        'mental_health_screen',                                         toggle_button
        'mental_health_issue_identified',                               toggle_button
        'mental_health_issues',                                         single_choice_multiple_toggle_button
        'global_developmental_delay_or_learning_difficulties',          toggle_button
        'global_developmental_delay_or_learning_difficulties_severity', single_choice_multiple_toggle_button
        'autistic_spectrum_disorder',                                   toggle_button
    ]

    [x] Assert user can change 'epilepsy_cause_known' to True
    [x] Assert user can change 'epilepsy_cause_known' to False
    [x] Assert user can change 'epilepsy_cause' to Aicardi's Syndrome (pk=134)
    [x] Assert user can change 'epilepsy_cause_categories' to array of EPILEPSY_CAUSES[0][0]=='Gen' and EPILEPSY_CAUSES[1][0]=='Imm' and and EPILEPSY_CAUSES[5][0]=='Othe'
    [x] Assert user can change 'epilepsy_cause_categories' to array of EPILEPSY_CAUSES[2][0]=='Inf' and EPILEPSY_CAUSES[3][0]=='Met' and EPILEPSY_CAUSES[4][0]=='Str'
    [x] Assert user can change 'relevant_impairments_behavioural_educational' to True
    [x] Assert user can change 'relevant_impairments_behavioural_educational' to False
    [x] Assert user can change 'mental_health_issues' to NEUROPSYCHIATRIC[0][0]=='AxD' ('Anxiety disorder')
    [x] Assert user can change 'mental_health_issues' to NEUROPSYCHIATRIC[0][0]=='EmB' ('Emotional/ behavioural')
    [x] Assert user can change 'mental_health_issues' to NEUROPSYCHIATRIC[0][0]=='MoD' ('Mood disorder')
    [x] Assert user can change 'mental_health_issues' to NEUROPSYCHIATRIC[0][0]=='SHm' ('Self harm')
    [x] Assert user can change 'mental_health_issues' to NEUROPSYCHIATRIC[0][0]=='Oth' ('Other')
    [x] Assert user can change 'mental_health_screen' to True
    [x] Assert user can change 'mental_health_screen' to False
    [x] Assert user can change 'mental_health_issue_identified' to True
    [x] Assert user can change 'mental_health_issue_identified' to False
    [x] Assert user can change 'autistic_spectrum_disorder' to True
    [x] Assert user can change 'autistic_spectrum_disorder' to False
    [x] Assert user can change 'global_developmental_delay_or_learning_difficulties' to True
    [x] Assert user can change 'global_developmental_delay_or_learning_difficulties' to False
    [x] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[0][0]=='mild'
    [x] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[1][0]=='moderate'
    [x] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[2][0]=='severe'
    [x] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[3][0]=='profound'
    [x] Assert user can change 'global_developmental_delay_or_learning_difficulties_severity' to SEVERITY[4][0]=='uncertain'

# Episode
    for field in fields: [
        'seizure_onset_date',                                                date_field
        'seizure_onset_date_confidence',                                     single_choice_multiple_toggle_button
        'episode_definition',                                                select
        'has_description_of_the_episode_or_episodes_been_gathered',          toggle_button
        'edit_description',                                                  string - updated in view function
        'delete_description_keyword',                                        Keyword id - updated in view function
        'epilepsy_or_nonepilepsy_status',                                    single_choice_multiple_toggle_button
        'epileptic_seizure_onset_type',                                      single_choice_multiple_toggle_button
        'focal_onset_epilepsy_checked_changed',                              updated in view function
        'epileptic_generalised_onset',                                       select
        'nonepilepsy_generalised_onset',                                     multiple_choice_multiple_toggle_button
        'nonepileptic_seizure_type',                                         select
        'nonepileptic_seizure_subtype',                                      select
    ]
    [] Assert user can change 'seizure_onset_date' to today
    [x] Assert user can change 'seizure_onset_date_confidence' to DATE_ACCURACY[0][0]=='Apx' (Approximate)
    [x] Assert user can change 'seizure_onset_date_confidence' to DATE_ACCURACY[1][0]=='Exc' (Exact)
    [x] Assert user can change 'seizure_onset_date_confidence' to DATE_ACCURACY[2][0]=='NK' (Not Known)
    [x] Assert user can change 'episode_definition' to EPISODE_DEFINITION[0][0]=='a' ('This was a single episode')
    [x] Assert user can change 'episode_definition' to EPISODE_DEFINITION[1][0]=='b' ('This was a cluster within 24 hours')
    [x] Assert user can change 'episode_definition' to EPISODE_DEFINITION[2][0]=='c' ('These were 2 or more episodes more than 24 hours apart')
    [x] Assert user can change 'has_description_of_the_episode_or_episodes_been_gathered' to True
    [x] Assert user can delete 'gelastic' in 'delete_description_keyword' from ['gelastic', 'left']
    [] Assert user can change 'edit_description' to "Jacob fell to the floor and shook the left side of his body."
    [] Assert user can change 'edit_description' to "Jacob fell to the floor and shook the left side of his body."
    [x] Assert user can change 'epilepsy_or_nonepilepsy_status' to EPILEPSY_DIAGNOSIS_STATUS[0][0]=='E' (Epilepsy)
    [x] Assert user can change 'epilepsy_or_nonepilepsy_status' to EPILEPSY_DIAGNOSIS_STATUS[1][0]=='NE' (Epilepsy)
    [x] Assert user can change 'epilepsy_or_nonepilepsy_status' to EPILEPSY_DIAGNOSIS_STATUS[2][0]=='U' (Uncertain)
    [x] Assert user can change 'epileptic_seizure_onset_type' to EPILEPSY_SEIZURE_TYPE[0][0]=='FO' (Focal Onset)
    [x] Assert user can change 'epileptic_seizure_onset_type' to EPILEPSY_SEIZURE_TYPE[1][0]=='GO' (Generalised Onset)
    [x] Assert user can change 'epileptic_seizure_onset_type' to EPILEPSY_SEIZURE_TYPE[2][0]=='UO' (Unknown Onset)
    [x] Assert user can change 'epileptic_seizure_onset_type' to EPILEPSY_SEIZURE_TYPE[3][0]=='UC' (Unclassified)
    [] Assert user can change 'focal_onset_epilepsy_checked_changed' to ........
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[0][0]=='AEM' ('Absence with eyelid myoclonia')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[1][0]=='Ato' ('Atonic')]
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[2][0]=='Aab' ('Atypical absence')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[3][0]=='Clo' ('Clonic')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[4][0]=='EpS' ('Epileptic spasms')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[5][0]=='MyC' ('Myoclonic')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[6][0]=='MAb' ('Myoclonic absence')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[7][0]=='MTC' ('Myoclonic-tonic-clonic')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[8][0]=='MAt' ('Myoclonic-atonic')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[9][0]=='Ton' ('Tonic')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[10][0]=='TCl' ('Tonic-clonic')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[11][0]=='TAb' ('Typical absence')
    [x] Assert user can change 'epileptic_generalised_onset' to GENERALISED_SEIZURE_TYPE[12][0]=='Oth' ('Other')
    [x] Assert user can change 'nonepileptic_seizure_type' to NON_EPILEPSY_SEIZURE_ONSET[0][0]=='BAr' ('Behaviour arrest')
    [x] Assert user can change 'nonepileptic_seizure_type' to NON_EPILEPSY_SEIZURE_ONSET[1][0]=='EpS' ('Epileptic spasms')
    [x] Assert user can change 'nonepileptic_seizure_type' to NON_EPILEPSY_SEIZURE_ONSET[2][0]=='TCl' ('Tonic-clonic')
    [x] Assert user can change 'nonepileptic_seizure_type' to NON_EPILEPSY_SEIZURE_ONSET[3][0]=='Oth' ('Other')
    [x] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[0][0]=='BPP' ('Behavioral Psychological And Psychiatric Disorders')
    [x] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[1][0]=='MAD' ('Migraine Associated Disorders')
    [x] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[2][0]=='ME' ('Miscellaneous Events')
    [x] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[3][0]=='SRC' ('Sleep Related Conditions')
    [x] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[4][0]=='SAS' ('Syncope And Anoxic Seizures')
    [x] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[5][0]=='PMD' ('Paroxysmal Movement Disorders')]], tuple[Literal['Oth'], Literal['Other']]]
    [x] Assert user can change 'nonepileptic_seizure_subtype' to NON_EPILEPSY_SEIZURE_TYPE[6][0]=='Oth' ('Other')

    
    [] Assert user cannot change 'seizure_onset_date' to before Case.date_of_birth (raise ValidationError)
    [] Assert user cannot change 'seizure_onset_date' to before Registration.first_paediatric_assessment_date (raise ValidationError)
    [] Assert user cannot change 'seizure_onset_date' to future date (raise ValidationError)
    

# Comorbidity
    for field in fields: [
        'comorbidity_diagnosis_date',                                       date_field
        'comorbidity_diagnosis',                                            select
    ]
    [] Assert user can change 'comorbidity_diagnosis_date' ..
    [x] Assert user can change 'comorbidity_diagnosis' ..

# Syndrome
    for field in fields: [
        add_syndrome                (multiaxial_diagnosis_id)               button click
        edit_syndrome               (syndrome_id)                           button click
        remove_syndrome             (syndrome_id)                           button click
        close_syndrome              (syndrome_id)                           button click
        syndrome_present            (multiaxial_diagnosis_id)               button click
        syndrome_diagnosis_date     (syndrome_id)                           date_field
        syndrome_name               (syndrome_id)                           select
    ]
    [] Assert user can change  ..
    [] Assert user can change  ..
    

# Assessment
    for field in fields: [
        'consultant_paediatrician_referral_made',                               toggle_button
        'consultant_paediatrician_referral_date',                               date_field
        'consultant_paediatrician_input_date',                                  date_field
        'general_paediatric_centre',                                            button click
        'edit_general_paediatric_centre',                                       button click
        'update_general_paediatric_centre_pressed',                             button click (action:edit/cancel)
        'paediatric_neurologist_referral_made',                                 toggle_button
        'paediatric_neurologist_referral_date',                                 date_field
        'paediatric_neurologist_input_date',                                    date_field
        'paediatric_neurology_centre',                                          button click
        'edit_paediatric_neurology_centre',                                     button click    
        'update_paediatric_neurology_centre_pressed',                           button click (action:edit/cancel)
        'childrens_epilepsy_surgical_service_referral_criteria_met',            toggle_button                
        'childrens_epilepsy_surgical_service_referral_made',                    toggle_button        
        'childrens_epilepsy_surgical_service_referral_date',                    date_field    
        'childrens_epilepsy_surgical_service_input_date',                       date_field
        'epilepsy_surgery_centre',                                              button click
        'edit_epilepsy_surgery_centre',                                         button click
        'update_epilepsy_surgery_centre_pressed',                               button click (action:edit/cancel)            
        'epilepsy_specialist_nurse_referral_made',                              toggle_button
        'epilepsy_specialist_nurse_referral_date',                              date_field    
        'epilepsy_specialist_nurse_input_date',                                 date_field
    ]
    [x] Assert user can change 'consultant_paediatrician_referral_made' to True
    [x] Assert user can change 'consultant_paediatrician_referral_made' to False
    [] Assert user can change 'consultant_paediatrician_referral_date' ..
    [] Assert user can change 'general_paediatric_centre'...
    [] Assert user can change 'edit_general_paediatric_centre' ..
    [] Assert user can change 'update_general_paediatric_centre_pressed'..
    [x] Assert user can change 'paediatric_neurologist_referral_made' to True
    [x] Assert user can change 'paediatric_neurologist_referral_made' to False
    [] Assert user can change 'paediatric_neurologist_referral_date' ..
    [] Assert user can change 'paediatric_neurologist_referral_date' ..
    [] Assert user can change 'paediatric_neurologist_input_date' ..
    [] Assert user can change 'paediatric_neurology_centre' ..
    [] Assert user can change 'edit_paediatric_neurology_centre' ..
    [] Assert user can change 'update_paediatric_neurology_centre_pressed'..
    [x] Assert user can change 'childrens_epilepsy_surgical_service_referral_criteria_met' to True
    [x] Assert user can change 'childrens_epilepsy_surgical_service_referral_criteria_met' to False
    [] Assert user can change 'childrens_epilepsy_surgical_service_referral_made' to True
    [] Assert user can change 'childrens_epilepsy_surgical_service_referral_made' to False
    [] Assert user can change 'childrens_epilepsy_surgical_service_referral_date' ..
    [] Assert user can change 'childrens_epilepsy_surgical_service_input_date' ..
    [] Assert user can change 'epilepsy_surgery_centre' ..
    [] Assert user can change 'edit_epilepsy_surgery_centre'..
    [] Assert user can change 'update_epilepsy_surgery_centre_pressed' ..
    [] Assert user can change 'update_epilepsy_surgery_centre_pressed' ..
    [x] Assert user can change 'epilepsy_specialist_nurse_referral_made' to True
    [x] Assert user can change 'epilepsy_specialist_nurse_referral_made' to False
    [] Assert user can change 'epilepsy_specialist_nurse_referral_date' ..
    [] Assert user can change 'epilepsy_specialist_nurse_input_date' ..

# Investigations
    for field in fields: [
        'eeg_indicated',                                                        toggle_button
        'eeg_request_date',                                                     date_field
        'eeg_performed_date',                                                   date_field    
        'eeg_declined',                                                         button click (confirm:edit/decline)
        'twelve_lead_ecg_status',                                               toggle_button        
        'ct_head_scan_status',                                                  toggle_button    
        'mri_indicated',                                                        toggle_button
        'mri_brain_requested_date',                                             date_field
        'mri_brain_reported_date',                                              date_field
        'mri_brain_declined',                                                   button click (confirm:edit/decline)
    ]
    [x] Assert user can change 'eeg_indicated' to True
    [x] Assert user can change 'eeg_indicated' to False
    [] Assert user can change 'eeg_request_date' ..
    [] Assert user can change 'eeg_performed_date' ..
    [] Assert user can change 'eeg_declined' ..
    [x] Assert user can change 'twelve_lead_ecg_status' to True
    [x] Assert user can change 'twelve_lead_ecg_status' to False
    [x] Assert user can change 'ct_head_scan_status' to True
    [x] Assert user can change 'ct_head_scan_status' to False
    [x] Assert user can change 'mri_indicated' to True
    [x] Assert user can change 'mri_indicated' to False
    [] Assert user can change 'mri_brain_requested_date' ..
    [] Assert user can change 'mri_brain_reported_date' ..
    [] Assert user can change 'mri_brain_declined' ..

# Management
    for field in fields: [
        'individualised_care_plan_in_place',                                    toggle_button
        'individualised_care_plan_date',                                        date_field
        'individualised_care_plan_has_parent_carer_child_agreement',            toggle_button
        'individualised_care_plan_includes_service_contact_details',            toggle_button
        'individualised_care_plan_include_first_aid',                           toggle_button
        'individualised_care_plan_parental_prolonged_seizure_care',             toggle_button
        'individualised_care_plan_includes_general_participation_risk',         toggle_button
        'individualised_care_plan_addresses_water_safety',                      toggle_button
        'individualised_care_plan_addresses_sudep',                             toggle_button    
        'individualised_care_plan_includes_ehcp',                               toggle_button    
        'has_individualised_care_plan_been_updated_in_the_last_year',           toggle_button                        
        'has_been_referred_for_mental_health_support',                          toggle_button        
        'has_support_for_mental_health_support',                                toggle_button
        'has_an_aed_been_given',                                                toggle_button
        'has_rescue_medication_been_prescribed',                                toggle_button
    ]
    [x] Assert user can change 'individualised_care_plan_in_place' to True
    [x] Assert user can change 'individualised_care_plan_in_place' to False
    [] Assert user can change 'individualised_care_plan_date' ..
    [x] Assert user can change 'individualised_care_plan_has_parent_carer_child_agreement' to True
    [x] Assert user can change 'individualised_care_plan_has_parent_carer_child_agreement' to False
    [x] Assert user can change 'individualised_care_plan_includes_service_contact_details' to True
    [x] Assert user can change 'individualised_care_plan_includes_service_contact_details' to False
    [x] Assert user can change 'individualised_care_plan_include_first_aid' to True
    [x] Assert user can change 'individualised_care_plan_include_first_aid' to False
    [x] Assert user can change 'individualised_care_plan_parental_prolonged_seizure_care' to True
    [x] Assert user can change 'individualised_care_plan_parental_prolonged_seizure_care' to False
    [x] Assert user can change 'individualised_care_plan_includes_general_participation_risk' to True
    [x] Assert user can change 'individualised_care_plan_includes_general_participation_risk' to False
    [x] Assert user can change 'individualised_care_plan_addresses_water_safety' to True
    [x] Assert user can change 'individualised_care_plan_addresses_water_safety' to False
    [x] Assert user can change 'individualised_care_plan_addresses_sudep' to True
    [x] Assert user can change 'individualised_care_plan_addresses_sudep' to False
    [x] Assert user can change 'individualised_care_plan_includes_ehcp' to True
    [x] Assert user can change 'individualised_care_plan_includes_ehcp' to False
    [x] Assert user can change 'has_individualised_care_plan_been_updated_in_the_last_year' to True
    [x] Assert user can change 'has_individualised_care_plan_been_updated_in_the_last_year' to False
    [x] Assert user can change 'has_been_referred_for_mental_health_support' to True
    [x] Assert user can change 'has_been_referred_for_mental_health_support' to False
    [x] Assert user can change 'has_support_for_mental_health_support' to True
    [x] Assert user can change 'has_support_for_mental_health_support' to False
    [x] Assert user can change 'has_an_aed_been_given' to True
    [x] Assert user can change 'has_an_aed_been_given' to False
    [x] Assert user can change 'has_rescue_medication_been_prescribed' to True
    [x] Assert user can change 'has_rescue_medication_been_prescribed' to False

# Antiepilepsy Medicine
    for field in fields: [
        'edit_antiepilepsy_medicine',                                           button click (antiepilepsy_medicine_id)
        'medicine_id',                                                          post on select change handled in view
        'antiepilepsy_medicine_start_date',                                     date_field
        'antiepilepsy_medicine_add_stop_date',                                  button click (antiepilepsy_medicine_id)
        'antiepilepsy_medicine_remove_stop_date',                               button click (antiepilepsy_medicine_id)
        'antiepilepsy_medicine_stop_date',                                      date_field
        'antiepilepsy_medicine_risk_discussed',                                 toggle_button
        'is_a_pregnancy_prevention_programme_in_place',                         toggle_button
        'has_a_valproate_annual_risk_acknowledgement_form_been_completed',      toggle_button
    ]
    [] Assert user can change 'edit_antiepilepsy_medicine' ..
    [] Assert user can change 'medicine_id' ..
    [] Assert user can change 'antiepilepsy_medicine_start_date' ..
    [] Assert user can change 'antiepilepsy_medicine_add_stop_date' ..
    [] Assert user can change 'antiepilepsy_medicine_remove_stop_date' ..
    [] Assert user can change 'antiepilepsy_medicine_stop_date' ..
    [x] Assert user can change 'antiepilepsy_medicine_risk_discussed' to True
    [x] Assert user can change 'antiepilepsy_medicine_risk_discussed' to False
    [x] Assert user can change 'is_a_pregnancy_prevention_programme_in_place' to True
    [x] Assert user can change 'is_a_pregnancy_prevention_programme_in_place' to False
    [x] Assert user can change 'has_a_valproate_annual_risk_acknowledgement_form_been_completed' to True
    [x] Assert user can change 'has_a_valproate_annual_risk_acknowledgement_form_been_completed' to False

"""
# Python imports
from datetime import date
from dateutil import relativedelta

# Django imports
from django.urls import reverse
from django.apps import apps

# third party imports
import pytest
import factory

# E12 imports
from epilepsy12.tests.UserDataClasses import (
    test_user_rcpch_audit_team_data,
)
from epilepsy12.tests.factories import (
    E12UserFactory,
    E12CaseFactory,
    E12SiteFactory,
    E12AntiEpilepsyMedicineFactory,
)

# E12 imports
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    Case,
    Episode,
    Keyword,
    EpilepsyCause,
    MultiaxialDiagnosis,
    Comorbidity,
    ComorbidityList,
    Medicine,
    AntiEpilepsyMedicine,
    SyndromeList,
    Syndrome,
)

from epilepsy12.constants import (
    SEX_TYPE,
    CHRONICITY,
    OPT_OUT_UNCERTAIN,
    SEVERITY,
    EPILEPSY_CAUSES,
    NEUROPSYCHIATRIC,
    DATE_ACCURACY,
    EPILEPSY_DIAGNOSIS_STATUS,
    EPILEPSY_SEIZURE_TYPE,
    GENERALISED_SEIZURE_TYPE,
    EPISODE_DEFINITION,
    NON_EPILEPSY_SEIZURE_ONSET,
    NON_EPILEPSY_SEIZURE_TYPE,
)

MULTIPLE_CHOICE_MULTIPLE_TOGGLES = (
    {
        "field_name": "mental_health_issues",
        "choices": NEUROPSYCHIATRIC,
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
    },
)


SINGLE_CHOICE_MULTIPLE_TOGGLES = (
    {
        "field_name": "first_paediatric_assessment_in_acute_or_nonacute_setting",
        "param": "first_paediatric_assessment_id",
        "choices": CHRONICITY,
        "model": "firstpaediatricassessment",
    },
    {
        "field_name": "previous_febrile_seizure",
        "choices": OPT_OUT_UNCERTAIN,
        "param": "epilepsy_context_id",
        "model": "epilepsycontext",
    },
    {
        "field_name": "previous_acute_symptomatic_seizure",
        "choices": OPT_OUT_UNCERTAIN,
        "param": "epilepsy_context_id",
        "model": "epilepsycontext",
    },
    {
        "field_name": "is_there_a_family_history_of_epilepsy",
        "choices": OPT_OUT_UNCERTAIN,
        "param": "epilepsy_context_id",
        "model": "epilepsycontext",
    },
    {
        "field_name": "previous_neonatal_seizures",
        "choices": OPT_OUT_UNCERTAIN,
        "param": "epilepsy_context_id",
        "model": "epilepsycontext",
    },
    {
        "field_name": "experienced_prolonged_generalized_convulsive_seizures",
        "choices": OPT_OUT_UNCERTAIN,
        "param": "epilepsy_context_id",
        "model": "epilepsycontext",
    },
    {
        "field_name": "experienced_prolonged_focal_seizures",
        "choices": OPT_OUT_UNCERTAIN,
        "param": "epilepsy_context_id",
        "model": "epilepsycontext",
    },
    {
        "field_name": "global_developmental_delay_or_learning_difficulties_severity",
        "choices": SEVERITY,
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
    },
    {
        "field_name": "seizure_onset_date_confidence",
        "choices": DATE_ACCURACY,
        "param": "episode_id",
        "model": "episode",
    },
    {
        "field_name": "epilepsy_or_nonepilepsy_status",
        "choices": EPILEPSY_DIAGNOSIS_STATUS,
        "param": "episode_id",
        "model": "episode",
    },
    {
        "field_name": "epileptic_seizure_onset_type",
        "choices": EPILEPSY_SEIZURE_TYPE,
        "param": "episode_id",
        "model": "episode",
    },
)

TOGGLES = (
    {
        "field_name": "has_number_of_episodes_since_the_first_been_documented",
        "param": "first_paediatric_assessment_id",
        "model": "firstpaediatricassessment",
    },
    {
        "field_name": "general_examination_performed",
        "param": "first_paediatric_assessment_id",
        "model": "firstpaediatricassessment",
    },
    {
        "field_name": "neurological_examination_performed",
        "param": "first_paediatric_assessment_id",
        "model": "firstpaediatricassessment",
    },
    {
        "field_name": "developmental_learning_or_schooling_problems",
        "param": "first_paediatric_assessment_id",
        "model": "firstpaediatricassessment",
    },
    {
        "field_name": "behavioural_or_emotional_problems",
        "param": "first_paediatric_assessment_id",
        "model": "firstpaediatricassessment",
    },
    {
        "field_name": "were_any_of_the_epileptic_seizures_convulsive",
        "param": "epilepsy_context_id",
        "model": "epilepsycontext",
    },
    {
        "field_name": "diagnosis_of_epilepsy_withdrawn",
        "param": "epilepsy_context_id",
        "model": "epilepsycontext",
    },
    {
        "field_name": "epilepsy_cause_known",
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
    },
    {
        "field_name": "relevant_impairments_behavioural_educational",
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
    },
    {
        "field_name": "mental_health_screen",
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
    },
    {
        "field_name": "mental_health_issue_identified",
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
    },
    {
        "field_name": "global_developmental_delay_or_learning_difficulties",
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
    },
    {
        "field_name": "autistic_spectrum_disorder",
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
    },
    {
        "field_name": "has_description_of_the_episode_or_episodes_been_gathered",
        "param": "episode_id",
        "model": "episode",
    },
    {
        "field_name": "consultant_paediatrician_referral_made",
        "param": "assessment_id",
        "model": "assessment",
    },
    {
        "field_name": "paediatric_neurologist_referral_made",
        "param": "assessment_id",
        "model": "assessment",
    },
    {
        "field_name": "childrens_epilepsy_surgical_service_referral_criteria_met",
        "param": "assessment_id",
        "model": "assessment",
    },
    {
        "field_name": "childrens_epilepsy_surgical_service_referral_made",
        "param": "assessment_id",
        "model": "assessment",
    },
    {
        "field_name": "epilepsy_specialist_nurse_referral_made",
        "param": "assessment_id",
        "model": "assessment",
    },
    {
        "field_name": "eeg_indicated",
        "param": "investigations_id",
        "model": "investigations",
    },
    {
        "field_name": "twelve_lead_ecg_status",
        "param": "investigations_id",
        "model": "investigations",
    },
    {
        "field_name": "ct_head_scan_status",
        "param": "investigations_id",
        "model": "investigations",
    },
    {
        "field_name": "mri_indicated",
        "param": "investigations_id",
        "model": "investigations",
    },
    {
        "field_name": "individualised_care_plan_in_place",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "individualised_care_plan_has_parent_carer_child_agreement",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "individualised_care_plan_includes_service_contact_details",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "individualised_care_plan_include_first_aid",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "individualised_care_plan_parental_prolonged_seizure_care",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "individualised_care_plan_includes_general_participation_risk",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "individualised_care_plan_addresses_water_safety",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "individualised_care_plan_addresses_sudep",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "individualised_care_plan_includes_ehcp",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "has_individualised_care_plan_been_updated_in_the_last_year",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "has_been_referred_for_mental_health_support",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "has_support_for_mental_health_support",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "has_an_aed_been_given",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "has_rescue_medication_been_prescribed",
        "param": "management_id",
        "model": "management",
    },
    {
        "field_name": "antiepilepsy_medicine_risk_discussed",
        "param": "antiepilepsy_medicine_id",
        "model": "antiepilepsymedicine",
    },
    {
        "field_name": "is_a_pregnancy_prevention_programme_in_place",
        "param": "antiepilepsy_medicine_id",
        "model": "antiepilepsymedicine",
    },
    {
        "field_name": "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
        "param": "antiepilepsy_medicine_id",
        "model": "antiepilepsymedicine",
    },
)

SELECTS = (
    {
        "field_name": "epilepsy_cause",
        "param": "multiaxial_diagnosis_id",
        "model": "multiaxialdiagnosis",
        "choices": None,
    },
    {
        "field_name": "comorbidity_diagnosis",
        "param": "comorbidity_id",
        "model": "comorbidity",
        "choices": None,
    },
    {
        "field_name": "episode_definition",
        "param": "episode_id",
        "model": "episode",
        "choices": EPISODE_DEFINITION,
    },
    {
        "field_name": "nonepileptic_seizure_type",
        "param": "episode_id",
        "model": "episode",
        "choices": NON_EPILEPSY_SEIZURE_ONSET,
    },
    {
        "field_name": "nonepileptic_seizure_subtype",
        "param": "episode_id",
        "model": "episode",
        "choices": NON_EPILEPSY_SEIZURE_TYPE,
    },
    {
        "field_name": "epileptic_generalised_onset",
        "choices": GENERALISED_SEIZURE_TYPE,
        "param": "episode_id",
        "model": "episode",
    },
    {
        "field_name": "syndrome_name",
        "choices": None,
        "param": "syndrome_id",
        "model": "syndrome",
    },
)


@pytest.mark.django_db
def test_user_updates_single_choice_multiple_toggle_success(
    client, seed_groups_fixture, seed_users_fixture, seed_cases_fixture
):
    """
    Assert for each single_choice_multiple_toggle choice selection, value stored in model is correct selection value
    """
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, url in enumerate(SINGLE_CHOICE_MULTIPLE_TOGGLES):
        for item in enumerate(url.get("choices")):
            model = get_model_from_model(
                case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
            )
            client.post(
                reverse(
                    url.get("field_name"),
                    kwargs={url.get("param"): model.id},
                ),
                headers={"Hx-Trigger-Name": item[0], "Hx-Request": "true"},
            )
            updated_model = get_model_from_model(
                case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
            )
            validate_single_choice_multiple_toggle_button(
                field_name=url.get("field_name"),
                model_instance=updated_model,
                expected_result=item[0],
                assert_pass=True,
            )


@pytest.mark.django_db
def test_user_updates_single_choice_multiple_toggle_fail(
    client, seed_groups_fixture, seed_users_fixture, seed_cases_fixture
):
    """
    Assert for each single_choice_multiple_toggle choice selection, value stored in model is correct selection value
    """
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, url in enumerate(SINGLE_CHOICE_MULTIPLE_TOGGLES):
        for item in enumerate(url.get("choices")):
            model = get_model_from_model(
                case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
            )
            client.post(
                reverse(
                    url.get("field_name"),
                    kwargs={url.get("param"): model.id},
                ),
                headers={"Hx-Trigger-Name": item[0], "Hx-Request": "true"},
            )
            updated_model = get_model_from_model(
                case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
            )
            validate_single_choice_multiple_toggle_button(
                field_name=url.get("field_name"),
                model_instance=updated_model,
                expected_result="dummy data",
                assert_pass=False,
            )


@pytest.mark.django_db
def test_user_updates_toggles_true_success(client):
    """
    Assert for each toggle selection, value stored in model is correct selection value
    """
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, url in enumerate(TOGGLES):
        print(url.get("field_name"))
        model = get_model_from_model(
            case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
        )
        client.post(
            reverse(
                url.get("field_name"),
                kwargs={url.get("param"): model.id},
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )
        updated_model = get_model_from_model(
            case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
        )
        validate_toggle_button(
            field_name=url.get("field_name"),
            model_instance=updated_model,
            expected_result=True,
            assert_pass=True,
        )


@pytest.mark.django_db
def test_user_updates_toggles_false_success(client):
    """
    Assert for each toggle selection, value stored in model is correct selection value
    """
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, url in enumerate(TOGGLES):
        model = get_model_from_model(
            case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
        )
        client.post(
            reverse(
                url.get("field_name"),
                kwargs={url.get("param"): model.id},
            ),
            headers={"Hx-Trigger-Name": "button-false", "Hx-Request": "true"},
        )
        updated_model = get_model_from_model(
            case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
        )
        validate_toggle_button(
            field_name=url.get("field_name"),
            model_instance=updated_model,
            expected_result=False,
            assert_pass=True,
        )


@pytest.mark.django_db
def test_user_updates_toggles_true_fail(client):
    """
    Assert for each toggle selection, value stored in model is correct selection value
    """
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, url in enumerate(TOGGLES):
        model = get_model_from_model(
            case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
        )
        client.post(
            reverse(
                url.get("field_name"),
                kwargs={url.get("param"): model.id},
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )
        updated_model = get_model_from_model(
            case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
        )
        validate_toggle_button(
            field_name=url.get("field_name"),
            model_instance=updated_model,
            expected_result=False,
            assert_pass=False,
        )


@pytest.mark.django_db
def test_user_updates_toggles_false_fail(client):
    """
    Assert for each toggle selection, value stored in model is correct selection value
    """
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, url in enumerate(TOGGLES):
        model = get_model_from_model(
            case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
        )
        client.post(
            reverse(
                url.get("field_name"),
                kwargs={url.get("param"): model.id},
            ),
            headers={"Hx-Trigger-Name": "button-false", "Hx-Request": "true"},
        )
        updated_model = get_model_from_model(
            case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
        )
        validate_toggle_button(
            field_name=url.get("field_name"),
            model_instance=updated_model,
            expected_result=True,
            assert_pass=False,
        )


@pytest.mark.skip(reason="unfinished test")
@pytest.mark.django_db
def test_user_updates_select_success(
    client,
):
    """
    Assert for each single_choice_multiple_toggle choice selection, value stored in model is correct selection value
    """
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, url in enumerate(SELECTS):
        if url.get("choices") is not None:
            for choice in url.get("choices"):
                model = get_model_from_model(
                    case=CASE_FROM_TEST_USER_ORGANISATION,
                    model_name=url.get("model"),
                )
                data = {url.get("field_name"): choice}

                client.post(
                    reverse(
                        url.get("field_name"),
                        kwargs={url.get("param"): model.id},
                    ),
                    headers={
                        "Hx-Trigger-Name": choice,
                        "Hx-Request": "true",
                    },
                    data=data,
                )
                updated_model = get_model_from_model(
                    case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
                )
                validate_select(
                    field_name=url.get("field_name"),
                    model_instance=updated_model,
                    expected_result=Comorbidity.objects.get(pk=134),  # Aicardi's sy.
                    assert_pass=True,
                )
        else:
            model = get_model_from_model(
                case=CASE_FROM_TEST_USER_ORGANISATION,
                model_name=url.get("model"),
            )

            if url.get("field_name") == "epilepsy_cause":
                data = {"epilepsy_cause": 134}
                expected_result = EpilepsyCause.objects.get(pk=134)  # Aicardi's sy
                htmx_trigger = "epilepsy_cause"
            elif url.get("field_name") == "comorbidity":
                data = {"comorbidityentity": 134}
                expected_result = ComorbidityList.objects.get(
                    pk=34
                )  # specific learning difficulty
                htmx_trigger = "comorbidityentity"
            elif url.get("field_name") == "syndrome_name":
                data = {"syndrome": 35}
                expected_result = SyndromeList.objects.get(
                    pk=35
                )  # Self-limited (familial) neonatal epilepsy
                htmx_trigger = "syndrome"

            client.post(
                reverse(
                    url.get("field_name"),
                    kwargs={url.get("param"): model.id},
                ),
                headers={"Hx-Trigger-Name": htmx_trigger, "Hx-Request": "true"},
                data=data,
            )
            updated_model = get_model_from_model(
                case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
            )
            validate_select(
                field_name=url.get("field_name"),
                model_instance=updated_model,
                expected_result=expected_result,
                assert_pass=True,
            )


@pytest.mark.django_db
def test_user_updates_select_fail(
    client,
):
    """
    Assert for each single_choice_multiple_toggle choice selection, value stored in model is correct selection value
    """
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    for index, url in enumerate(SELECTS):
        if url.get("choices") is not None:
            for choice in url.get("choices"):
                model = get_model_from_model(
                    case=CASE_FROM_TEST_USER_ORGANISATION,
                    model_name=url.get("model"),
                )
                data = {url.get("field_name"): choice}

                client.post(
                    reverse(
                        url.get("field_name"),
                        kwargs={url.get("param"): model.id},
                    ),
                    headers={
                        "Hx-Trigger-Name": choice,
                        "Hx-Request": "true",
                    },
                    data=data,
                )
                updated_model = get_model_from_model(
                    case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
                )
                validate_select(
                    field_name=url.get("field_name"),
                    model_instance=updated_model,
                    expected_result=ComorbidityList.objects.get(
                        pk=135
                    ),  # Dysmorphic sialidosis with renal involvement
                    assert_pass=False,
                )
        else:
            model = get_model_from_model(
                case=CASE_FROM_TEST_USER_ORGANISATION,
                model_name=url.get("model"),
            )

            if url.get("field_name") == "epilepsy_cause":
                data = {"epilepsy_cause": 134}  # Aicardi's sy.
                expected_result = EpilepsyCause.objects.get(
                    pk=135
                )  # Dysmorphic sialidosis with renal involvement
                htmx_trigger = "epilepsy_cause"
            elif url.get("field_name") == "comorbidity_diagnosis":
                data = {"comorbidityentity": 134}
                expected_result = ComorbidityList.objects.get(
                    pk=35
                )  # Meets criteria for referral to Children's Epilepsy Surgery Service
                htmx_trigger = "comorbidityentity"
            elif url.get("field_name") == "syndrome_name":
                data = {"syndrome": 35}
                expected_result = SyndromeList.objects.get(
                    pk=34
                )  # Self-limited (familial) neonatal epilepsy
                htmx_trigger = "syndrome"

            client.post(
                reverse(
                    url.get("field_name"),
                    kwargs={url.get("param"): model.id},
                ),
                headers={"Hx-Trigger-Name": htmx_trigger, "Hx-Request": "true"},
                data=data,
            )
            updated_model = get_model_from_model(
                case=CASE_FROM_TEST_USER_ORGANISATION, model_name=url.get("model")
            )
            validate_select(
                field_name=url.get("field_name"),
                model_instance=updated_model,
                expected_result=expected_result,
                assert_pass=False,
            )


@pytest.mark.django_db
def test_age_at_registration_cannot_be_gt_24yo(client, GOSH):
    """
    Assert date of first paediatric assessment cannot be after 24th birthday
    """

    FIRST_PAEDIATRIC_ASSESSMENT_DATE = date(2023, 1, 1)
    DATE_OF_BIRTH = FIRST_PAEDIATRIC_ASSESSMENT_DATE - relativedelta.relativedelta(
        years=24
    )

    # GOSH
    TEST_USER_ORGANISATION = GOSH

    CASE_FROM_TEST_USER_ORGANISATION = E12CaseFactory.create(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
        date_of_birth=DATE_OF_BIRTH,
        registration__first_paediatric_assessment_date=None,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    response = client.post(
        reverse(
            "first_paediatric_assessment_date",
            kwargs={"case_id": CASE_FROM_TEST_USER_ORGANISATION.id},
        ),
        headers={
            "Hx-Trigger-Name": "first_paediatric_assessment_date",
            "Hx-Request": "true",
        },
        data={"first_paediatric_assessment_date": FIRST_PAEDIATRIC_ASSESSMENT_DATE},
    )

    err_msg = response.context["error_message"]

    assert isinstance(err_msg, ValueError)
    assert (
        str(err_msg)
        == "To be included in Epilepsy12, child_GREAT ORMOND STREET HOSPITAL CENTRAL LONDON SITE Anderson cannot be over 24y at first paediatric assessment."
    )


# Test helper methods - there is one for each page_element
def validate_date_assertions(
    field_name: str,
    model_instance,
    case,
    second_date: date = None,
    is_initial_date=False,
    assert_pass=True,
):
    """
    Tests all dates
    """

    date_to_test: date = getattr(model_instance, field_name, None)

    if date_to_test is None or type(date_to_test) is not date:
        raise Exception("This field either does not exist or is not a date.")

    if assert_pass:
        assert (
            date_to_test <= date.today()
        ), f"{field_name} - {date_to_test} is not in the future - Expected PASS"
        assert (
            date_to_test >= case.date_of_birth
        ), f"{field_name} - {date_to_test} is not before {case}'s date of birth - Expected PASS"
        assert (
            date_to_test >= case.registration.first_paediatric_assessment_date
        ), f"{date_to_test} is not before {case}'s first paediatric assessment date ({case.registration.first_paediatric_assessment_date}) - Expected PASS"
    else:
        assert (
            date_to_test > date.today()
        ), f"{field_name} - {date_to_test} is in the future - Expected FAIL"
        assert (
            date_to_test < case.date_of_birth
        ), f"{field_name} - {date_to_test} is before {case}'s date of birth - Expected FAIL"
        assert (
            date_to_test < case.registration.first_paediatric_assessment_date
        ), f"{field_name} - {date_to_test} is before {case}'s first paediatric assessment date ({case.registration.first_paediatric_assessment_date}) - Expected FAIL"

    if second_date is not None:
        if assert_pass:
            if is_initial_date:
                assert (
                    date_to_test <= second_date
                ), f"{field_name} - {date_to_test} is before {second_date} - Expected PASS"
            else:
                assert (
                    date_to_test >= second_date
                ), f"{field_name} - {date_to_test} is after {second_date} - Expected PASS"
        else:
            if is_initial_date:
                assert (
                    date_to_test > second_date
                ), f"{field_name} - {date_to_test} is not before {second_date} - Expected FAIL"
            else:
                assert (
                    date_to_test < second_date
                ), f"{field_name} - {date_to_test} is not after {second_date} - Expected FAIL"


def validate_toggle_button(
    field_name: str, model_instance, expected_result: bool, assert_pass=True
):
    """
    Asserts whether the result stored in the model matches that expected
    """
    field_value = getattr(model_instance, field_name, None)

    if field_value is not None:
        if assert_pass:
            assert (
                expected_result == field_value
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected PASS"
        else:
            assert (
                expected_result != field_value
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected Fail"


def validate_single_choice_multiple_toggle_button(
    field_name: str, model_instance, expected_result, assert_pass=True
):
    """
    Asserts whether the result stored in the model matches that expected
    """
    field_value = getattr(model_instance, field_name, None)

    if field_value is not None:
        if assert_pass:
            assert (
                f"{expected_result}" == f"{field_value}"
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected PASS"
        else:
            assert (
                f"{expected_result}" != f"{field_value}"
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected Fail"


def validate_select(field_name: str, model_instance, expected_result, assert_pass=True):
    """
    Asserts whether the result stored in the model matches that expected
    """
    field_value = getattr(model_instance, field_name, None)

    if field_value is not None:
        if assert_pass:
            assert (
                f"{expected_result}" == f"{field_value}"
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected PASS"
        else:
            assert (
                f"{expected_result}" != f"{field_value}"
            ), f"{field_name} - result stored in model is {field_value}. Result expected: {expected_result} - Expected Fail"


def get_model_from_model(case, model_name):
    """
    Return model instance related to Case
    """
    if model_name == "episode":
        return Episode.objects.filter(
            multiaxial_diagnosis=case.registration.multiaxialdiagnosis
        ).first()
    elif model_name == "comorbidity":
        comorbidity, created = Comorbidity.objects.get_or_create(
            multiaxial_diagnosis=case.registration.multiaxialdiagnosis,
            comorbidityentity=ComorbidityList.objects.get(
                pk=34
            ),  # specific learning difficulty
        )
        return comorbidity
    elif model_name == "syndrome":
        syndrome, created = Syndrome.objects.get_or_create(
            multiaxial_diagnosis=case.registration.multiaxialdiagnosis,
            syndrome=SyndromeList.objects.get(
                pk=35
            ),  # Self-limited (familial) neonatal epilepsy
        )
        return syndrome
    elif model_name == "epilepsycauseentity":
        return Comorbidity.objects.get(pk=135)  # Aicardi's syndrome
    elif model_name == "antiepilepsymedicine":
        return AntiEpilepsyMedicine.objects.create(
            management=case.registration.management,
            is_rescue_medicine=False,
            medicine_entity=Medicine.objects.get(medicine_name="Sodium valproate"),
        )
    elif model_name == "multiaxialdiagnosis":
        return MultiaxialDiagnosis.objects.get(
            pk=case.registration.multiaxialdiagnosis.pk
        )  #
    else:
        refresh_case = Case.objects.get(pk=case.pk)
        return getattr(refresh_case.registration, model_name, None)
