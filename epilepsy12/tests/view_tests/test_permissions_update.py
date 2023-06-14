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

# First Paediatric Assessment
for field in fields: [
    'first_paediatric_assessment_in_acute_or_nonacute_setting',
    'has_number_of_episodes_since_the_first_been_documented',
    'general_examination_performed',
    'neurological_examination_performed',
    'developmental_learning_or_schooling_problems',
    'behavioural_or_emotional_problems',
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


"""
