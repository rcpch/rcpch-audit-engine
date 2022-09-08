LEAD_CLINICIAN = 1
CENTRE_ADMINISTRATOR = 2
PAEDIATRIC_NEUROLOGIST = 3
GENERAL_PAEDIATRICIAN_WITH_EPILEPSY_INTEREST = 4
AUDIT_ANALYST = 5
AUDIT_ADMINISTRATOR = 6

ROLES = (
    (LEAD_CLINICIAN, "Lead Clinician"),
    (CENTRE_ADMINISTRATOR, "Centre Administrator"),
    (PAEDIATRIC_NEUROLOGIST, "Paediatric Neurologist"),
    (GENERAL_PAEDIATRICIAN_WITH_EPILEPSY_INTEREST,
     "General Paediatrician with expertise in Epilepsy"),
    (AUDIT_ANALYST, "Audit Analyst"),
    (AUDIT_ADMINISTRATOR, "Audit Administrator")
)

MR = 1
MRS = 2
MS = 3
DR = 4
PROFESSOR = 5

TITLES = (
    (MR, "Mr"),
    (MRS, "Mrs"),
    (MS, "Ms"),
    (DR, "Dr"),
    (PROFESSOR, "Professor")
)

"""
Groups
"""
# logged in user can view all national data but not logs
EPILEPSY12_AUDIT_TEAM_VIEW_ONLY = 'epilepsy12_audit_team_view_only'

# logged in user can edit but not delete national data. Cannot view or edit logs or permissions.
EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS = 'epilepsy12_audit_team_edit_access'

# logged in user access all areas: can create/update/delete any audit data, logs, epilepsy key words and hospital trusts, groups and permissions
EPILEPSY12_AUDIT_TEAM_FULL_ACCESS = 'epilepsy12_audit_team_full_access'

# logged in user can view all data relating to their trust(s) but not logs
TRUST_AUDIT_TEAM_VIEW_ONLY = 'trust_audit_team_view_only'

# logged in user can edit but not delete all data relating to their trust(s) but not view or edit logs, epilepsy key words and hospital trusts, groups and permissions
TRUST_AUDIT_TEAM_EDIT_ACCESS = 'trust_audit_team_edit_access'

# logged in user can delete all data relating to their trust(s) but not view or edit logs, epilepsy key words and hospital trusts, groups and permissions
TRUST_AUDIT_TEAM_FULL_ACCESS = 'trust_audit_team_full_access'

# logged in user can view their own audit data, consent to participation and remove that consent/opt out. Opting out would delete all data relating to them, except the epilepsy12 unique identifier
PATIENT_ACCESS = 'patient_access'

GROUPS = (
    EPILEPSY12_AUDIT_TEAM_VIEW_ONLY,
    EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    PATIENT_ACCESS,
)


CAN_VIEW_CHILD_NHS_NUMBER = (
    'can_view_child_nhs_number', 'Can view a child\'s NHS Number')
CAN_VIEW_CHILD_DATE_OF_BIRTH = (
    'can_view_child_date_of_birth', 'Can view a child\'s date of birth')
CAN_DELETE_CHILD_CASE_DATA = ('can_delete_child_case_data',
                              'Can irreversibly delete a child\'s case data.')
CAN_UPDATE_CHILD_CASE_DATA = ('can_update_child_case_data',
                              'Can edit or update a child\'s case data.')
CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING = ('can_lock_child_case_data_from_editing',
                                         'Can lock a child\'s record from editing.')
CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING = ('can_unlock_child_case_data_from_editing',
                                           'Can unlock a child\'s record from editing.')
CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT = ('can_opt_out_child_from_inclusion_in_audit',
                                             'Can sanction an opt out from participating in the audit. Note all the child\'s date except Epilepsy12 unique identifier are irretrievably deleted.')
CAN_VIEW_CHILD_CASE_DATA = ('can_view_child_case_data',
                            'Can view a child\'s demographic and case information.')
CAN_APPROVE_ELIGIBILITY = ('can_approve_eligibility',
                           'Can approve eligibility for Epilepsy12.')
CAN_REMOVE_APPROVAL_OF_ELIGIBILITY = ('can_remove_approval_of_eligibility',
                                      'Can remove approval of eligibiltiy for Epilepsy12.')
CAN_VIEW_LEAD_CLINICIAN = ('can_view_lead_clinician',
                           'Can view the lead clinician')
CAN_ALLOCATE_LEAD_CLINICIAN = (
    'can_allocate_lead_clinician', 'Can allocate the lead clinician.')
CAN_EDIT_LEAD_CLINICIAN = ('can_edit_lead_clinician',
                           'Can edit the lead clinician.')
CAN_REGISTER_CHILD_IN_EPILEPSY12 = ('can_register_child_in_epilepsy12',
                                    'Can register child in Epilepsy12. (A cohort number is automatically allocaeted)')
CAN_UNREGISTER_CHILD_IN_EPILEPSY12 = ('can_unregister_child_in_epilepsy12',
                                      'Can unregister a child in Epilepsy. Their record and previously entered data is untouched.')
CAN_VIEW_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS = ('can_view_first_paediatric_assessment_fields',
                                               'Can view all information gathered at first assessment.')
CAN_EDIT_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS = ('can_edit_first_paediatric_assessment_fields',
                                               'Can edit all information gathered at first assessment.')
CAN_VIEW_EPILEPSY_CONTEXT_FIELDS = ('can_view_epilepsy_context_fields',
                                    'Can view all fiedls related to epilepsy context.')
CAN_EDIT_EPILEPSY_CONTEXT_FIELDS = ('can_edit_epilepsy_context_fields',
                                    'Can edit all fields related to epilepsy context.')
CAN_VIEW_MULTIAXIAL_DIAGNOSIS_FIELDS = ('can_view_multiaxial_diagnosis_fields',
                                        'Can only view fields relating to multiaxial diagnosis.')
CAN_EDIT_MULTIAXIAL_DIAGNOSIS_FIELDS = ('can_edit_multiaxial_diagnosis_fields',
                                        'Can only create or edit fields relating to multiaxial diagnosis.')
CAN_VIEW_SEIZURE_EPISODES = (
    'can_view_seizure_episodes', 'Can only view seizure episodes')
CAN_ADD_SEIZURE_EPISODE = ('can_add_seizure_episode',
                           'Can add a new seizure episode')
CAN_UPDATE_SEIZURE_EPISODE = ('can_update_seizure_episode',
                              'Can edit or update a seizure episode but not delete.')
CAN_DELETE_SEIZURE_EPISODE = (
    'can_delete_seizure_episode', 'Can delete a seizure episode.')
CAN_ADD_SYNDROME = ('can_add_syndrome', 'Can add a new syndrome.')
CAN_EDIT_SYNDROME_FIELDS = ('can_edit_syndrome_fields',
                            'Can edit or update an epilepsy syndrome, but not delete.')
CAN_DELETE_SYNDROME = ('can_delete_syndrome',
                       'Can delete an epilepsy syndrome')
CAN_VIEW_COMORBIDITIES = ('can_view_comorbidities', 'Can view comorbidities')
CAN_ADD_COMORBIDITY = ('can_add_comorbidity', 'Can add a comorbidity')
CAN_EDIT_COMORBIDITY_FIELDS = ('can_edit_comorbidity_fields',
                               'Can edit or update but not delete a comorbidity.')
CAN_DELETE_COMORBIDITY = ('can_delete_comorbidity',
                          'Can delete a comorbidity.')
CAN_VIEW_MILESTONES = ('can_view_milestones',
                       'Can view milestones in Epilepsy12 audit.')
CAN_EDIT_MILESTONES_FIELDS = ('can_edit_milestones_fields',
                              'Can edit or update milestones in Epilepsy12 audit.')
CAN_VIEW_GENERAL_PAEDIATRIC_CENTRE = ('can_view_general_paediatric_centre',
                                      'Can view general paediatric centre.')
CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE = ('can_allocate_general_paediatric_centre',
                                          'Can allocate general paediatric centre.')
CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE = ('can_update_general_paediatric_centre',
                                        'Can edit or update but not delete general paediatric centre.')
CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE = ('can_delete_general_paediatric_centre',
                                        'Can delete general paediatric centre.')
CAN_VIEW_TERTIARY_NEUROLOGY_CENTRE = ('can_view_tertiary_neurology_centre',
                                      'Can view tertiary neurology centre.')
CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE = ('can_allocate_tertiary_neurology_centre',
                                          'Can allocate tertiary neurology centre.')
CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE = ('can_edit_tertiary_neurology_centre',
                                      'Can edit or update but not delete tertiary neurology centre.')
CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE = ('can_delete_tertiary_neurology_centre',
                                        'Can delete tertiary neurology centre.')
CAN_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE = ('can_view_childrens_epilepsy_surgery_centre',
                                              'Can view children\'s epilepsy surgery centre.')
CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE = ('can_allocate_childrens_epilepsy_surgery_centre',
                                                  'Can allocate children\'s epilepsy surgery centre.')
CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE = ('can_edit_childrens_epilepsy_surgery_centre',
                                              'Can edit or update but not delete children\'s epilepsy surgery centre.')
CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE = ('can_delete_childrens_epilepsy_surgery_centre',
                                                'Can delete children\'s epilepsy surgery centre.')
CAN_VIEW_INVESTIGATIONS_FIELDS = (
    'can_view_investigations_fields', 'Can view investigations.')
CAN_EDIT_INVESTIGATIONS_FIELDS = (
    'can_edit_investigations_fields', 'Can edit investigations.')
CAN_VIEW_MANAGEMENT_FIELDS = ('can_view_management_fields',
                              'Can view epilepsy management and care plans.')
CAN_EDIT_MANAGEMENT_FIELDS = ('can_edit_management_fields',
                              'Can edit or update epilepsy management and care plans.')
CAN_VIEW_ANTIEPILEPSY_MEDICINES = ('can_view_antiepilepsy_medicines',
                                   'Can only view antiepilepsy medicines.')
CAN_EDIT_ANTIEPILEPSY_MEDICINES = ('can_edit_antiepilepsy_medicines',
                                   'Can edit or update but not delete antiepilepsy medicines.')
CAN_DELETE_ANTIEPILEPSY_MEDICINES = ('can_delete_antiepilepsy_medicines',
                                     'Can delete antiepilepsy medicines.')
CAN_VIEW_RESCUE_MEDICINES = (
    'can_view_rescue_medicines', 'Can only view rescue medicines.')
CAN_EDIT_RESCUE_MEDICINES = ('can_edit_rescue_medicines',
                             'Can edit or update but not delete rescue medicines.')
CAN_DELETE_RESCUE_MEDICINES = (
    'can_delete_rescue_medicines', 'Can delete rescue medicines.')

CAN_ADD_HOSPITAL_TRUSTS = ('can_add_hospital_trusts',
                           'Can add a new hospital trust.')
CAN_EDIT_HOSPITAL_TRUSTS = ('can_edit_hospital_trusts',
                            'Can edit or update a hospital trust\'s details.')
CAN_DELETE_HOSPITAL_TRUSTS = ('can_delete_hospital_trusts',
                              'Can delete a hospital trust or its details.')
CAN_ADD_KEYWORDS = ('can_add_keywords', 'Can add new semiology key words.')
CAN_EDIT_KEYWORDS = ('can_edit_keywords',
                     'Can edit or update but not delete semiology key words.')
CAN_DELETE_KEYWORDS = ('can_delete_keywords',
                       'Can delete semiology key words.')
CAN_CONSENT_TO_AUDIT_PARTICIPATION = ('can_consent_to_audit_participation',
                                      'Can consent to participating in Epilepsy12.')

PERMISSIONS = (
    CAN_VIEW_CHILD_NHS_NUMBER,
    CAN_VIEW_CHILD_DATE_OF_BIRTH,
    CAN_DELETE_CHILD_CASE_DATA,
    CAN_UPDATE_CHILD_CASE_DATA,
    CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
    CAN_VIEW_CHILD_CASE_DATA,
    CAN_APPROVE_ELIGIBILITY,
    CAN_REMOVE_APPROVAL_OF_ELIGIBILITY,
    CAN_VIEW_LEAD_CLINICIAN,
    CAN_ALLOCATE_LEAD_CLINICIAN,
    CAN_EDIT_LEAD_CLINICIAN,
    CAN_REGISTER_CHILD_IN_EPILEPSY12,
    CAN_UNREGISTER_CHILD_IN_EPILEPSY12,
    CAN_VIEW_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS,
    CAN_EDIT_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS,
    CAN_VIEW_EPILEPSY_CONTEXT_FIELDS,
    CAN_EDIT_EPILEPSY_CONTEXT_FIELDS,
    CAN_VIEW_MULTIAXIAL_DIAGNOSIS_FIELDS,
    CAN_EDIT_MULTIAXIAL_DIAGNOSIS_FIELDS,
    CAN_VIEW_SEIZURE_EPISODES,
    CAN_ADD_SEIZURE_EPISODE,
    CAN_UPDATE_SEIZURE_EPISODE,
    CAN_DELETE_SEIZURE_EPISODE,
    CAN_ADD_SYNDROME,
    CAN_EDIT_SYNDROME_FIELDS,
    CAN_DELETE_SYNDROME,
    CAN_VIEW_COMORBIDITIES,
    CAN_ADD_COMORBIDITY,
    CAN_EDIT_COMORBIDITY_FIELDS,
    CAN_DELETE_COMORBIDITY,
    CAN_VIEW_MILESTONES,
    CAN_EDIT_MILESTONES_FIELDS,
    CAN_VIEW_GENERAL_PAEDIATRIC_CENTRE,
    CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_VIEW_TERTIARY_NEUROLOGY_CENTRE,
    CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE,
    CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE,
    CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE,
    CAN_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_VIEW_INVESTIGATIONS_FIELDS,
    CAN_EDIT_INVESTIGATIONS_FIELDS,
    CAN_VIEW_MANAGEMENT_FIELDS,
    CAN_EDIT_MANAGEMENT_FIELDS,
    CAN_VIEW_ANTIEPILEPSY_MEDICINES,
    CAN_EDIT_ANTIEPILEPSY_MEDICINES,
    CAN_DELETE_ANTIEPILEPSY_MEDICINES,
    CAN_VIEW_RESCUE_MEDICINES,
    CAN_EDIT_RESCUE_MEDICINES,
    CAN_DELETE_RESCUE_MEDICINES,
    CAN_ADD_HOSPITAL_TRUSTS,
    CAN_EDIT_HOSPITAL_TRUSTS,
    CAN_DELETE_HOSPITAL_TRUSTS,
    CAN_ADD_KEYWORDS,
    CAN_EDIT_KEYWORDS,
    CAN_DELETE_KEYWORDS,
)

EPILEPSY12_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS = [
    CAN_VIEW_CHILD_CASE_DATA,
    CAN_VIEW_LEAD_CLINICIAN,
    CAN_VIEW_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS,
    CAN_VIEW_EPILEPSY_CONTEXT_FIELDS,
    CAN_VIEW_MULTIAXIAL_DIAGNOSIS_FIELDS,
    CAN_VIEW_SEIZURE_EPISODES,
    CAN_VIEW_COMORBIDITIES,
    CAN_VIEW_GENERAL_PAEDIATRIC_CENTRE,
    CAN_VIEW_TERTIARY_NEUROLOGY_CENTRE,
    CAN_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_VIEW_INVESTIGATIONS_FIELDS,
    CAN_VIEW_ANTIEPILEPSY_MEDICINES,
    CAN_VIEW_RESCUE_MEDICINES,
]

EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS = [
    CAN_VIEW_CHILD_NHS_NUMBER,
    CAN_VIEW_CHILD_DATE_OF_BIRTH,
    CAN_UPDATE_CHILD_CASE_DATA,
    CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_APPROVE_ELIGIBILITY,
    CAN_ALLOCATE_LEAD_CLINICIAN,
    CAN_EDIT_LEAD_CLINICIAN,
    CAN_REGISTER_CHILD_IN_EPILEPSY12,
    CAN_EDIT_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS,
    CAN_EDIT_EPILEPSY_CONTEXT_FIELDS,
    CAN_EDIT_MULTIAXIAL_DIAGNOSIS_FIELDS,
    CAN_ADD_SEIZURE_EPISODE,
    CAN_UPDATE_SEIZURE_EPISODE,
    CAN_ADD_SYNDROME,
    CAN_EDIT_SYNDROME_FIELDS,
    CAN_ADD_COMORBIDITY,
    CAN_EDIT_COMORBIDITY_FIELDS,
    CAN_EDIT_MILESTONES_FIELDS,
    CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE,
    CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE,
    CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_EDIT_INVESTIGATIONS_FIELDS,
    CAN_EDIT_MANAGEMENT_FIELDS,
    CAN_EDIT_ANTIEPILEPSY_MEDICINES,
    CAN_EDIT_RESCUE_MEDICINES,
]

EPILEPSY12_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS = [
    CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
    CAN_REMOVE_APPROVAL_OF_ELIGIBILITY,
    CAN_UNREGISTER_CHILD_IN_EPILEPSY12,
    CAN_DELETE_SEIZURE_EPISODE,
    CAN_DELETE_COMORBIDITY,
    CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE,
    CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_DELETE_ANTIEPILEPSY_MEDICINES,
    CAN_DELETE_RESCUE_MEDICINES,
    CAN_ADD_HOSPITAL_TRUSTS,
    CAN_EDIT_HOSPITAL_TRUSTS,
    CAN_DELETE_HOSPITAL_TRUSTS,
    CAN_EDIT_KEYWORDS,
    CAN_DELETE_KEYWORDS,
]

TRUST_AUDIT_TEAM_VIEW_ONLY_PERMISSIONS = [
    CAN_VIEW_CHILD_NHS_NUMBER,
    CAN_VIEW_CHILD_DATE_OF_BIRTH,
    CAN_UPDATE_CHILD_CASE_DATA,
    CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_APPROVE_ELIGIBILITY,
    CAN_ALLOCATE_LEAD_CLINICIAN,
    CAN_EDIT_LEAD_CLINICIAN,
    CAN_REGISTER_CHILD_IN_EPILEPSY12,
    CAN_EDIT_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS,
    CAN_EDIT_EPILEPSY_CONTEXT_FIELDS,
    CAN_EDIT_MULTIAXIAL_DIAGNOSIS_FIELDS,
    CAN_ADD_SEIZURE_EPISODE,
    CAN_UPDATE_SEIZURE_EPISODE,
    CAN_ADD_SYNDROME,
    CAN_EDIT_SYNDROME_FIELDS,
    CAN_ADD_COMORBIDITY,
    CAN_EDIT_COMORBIDITY_FIELDS,
    CAN_EDIT_MILESTONES_FIELDS,
    CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE,
    CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE,
    CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_EDIT_INVESTIGATIONS_FIELDS,
    CAN_EDIT_MANAGEMENT_FIELDS,
    CAN_EDIT_ANTIEPILEPSY_MEDICINES,
    CAN_EDIT_RESCUE_MEDICINES,
]

TRUST_AUDIT_TEAM_EDIT_ACCESS_PERMISSIONS = [
    CAN_VIEW_CHILD_NHS_NUMBER,
    CAN_VIEW_CHILD_DATE_OF_BIRTH,
    CAN_UPDATE_CHILD_CASE_DATA,
    CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_APPROVE_ELIGIBILITY,
    CAN_ALLOCATE_LEAD_CLINICIAN,
    CAN_EDIT_LEAD_CLINICIAN,
    CAN_REGISTER_CHILD_IN_EPILEPSY12,
    CAN_EDIT_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS,
    CAN_EDIT_EPILEPSY_CONTEXT_FIELDS,
    CAN_EDIT_MULTIAXIAL_DIAGNOSIS_FIELDS,
    CAN_ADD_SEIZURE_EPISODE,
    CAN_UPDATE_SEIZURE_EPISODE,
    CAN_ADD_SYNDROME,
    CAN_EDIT_SYNDROME_FIELDS,
    CAN_ADD_COMORBIDITY,
    CAN_EDIT_COMORBIDITY_FIELDS,
    CAN_EDIT_MILESTONES_FIELDS,
    CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE,
    CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE,
    CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_EDIT_INVESTIGATIONS_FIELDS,
    CAN_EDIT_MANAGEMENT_FIELDS,
    CAN_EDIT_ANTIEPILEPSY_MEDICINES,
    CAN_EDIT_RESCUE_MEDICINES,
]

TRUST_AUDIT_TEAM_FULL_ACCESS_PERMISSIONS = [
    CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
    CAN_REMOVE_APPROVAL_OF_ELIGIBILITY,
    CAN_UNREGISTER_CHILD_IN_EPILEPSY12,
    CAN_DELETE_SEIZURE_EPISODE,
    CAN_DELETE_COMORBIDITY,
    CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE,
    CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_DELETE_ANTIEPILEPSY_MEDICINES,
    CAN_DELETE_RESCUE_MEDICINES,
]

PATIENT_ACCESS_PERMISSIONS = [
    CAN_VIEW_CHILD_CASE_DATA,
    CAN_VIEW_LEAD_CLINICIAN,
    CAN_VIEW_FIRST_PAEDIATRIC_ASSESSMENT_FIELDS,
    CAN_VIEW_EPILEPSY_CONTEXT_FIELDS,
    CAN_VIEW_MULTIAXIAL_DIAGNOSIS_FIELDS,
    CAN_VIEW_SEIZURE_EPISODES,
    CAN_VIEW_COMORBIDITIES,
    CAN_VIEW_GENERAL_PAEDIATRIC_CENTRE,
    CAN_VIEW_TERTIARY_NEUROLOGY_CENTRE,
    CAN_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_VIEW_INVESTIGATIONS_FIELDS,
    CAN_VIEW_ANTIEPILEPSY_MEDICINES,
    CAN_VIEW_RESCUE_MEDICINES,
    CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
    CAN_CONSENT_TO_AUDIT_PARTICIPATION
]
