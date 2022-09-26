# LEAD_CLINICIAN = 1
# CENTRE_ADMINISTRATOR = 2
# PAEDIATRIC_NEUROLOGIST = 3
# GENERAL_PAEDIATRICIAN_WITH_EPILEPSY_INTEREST = 4
# AUDIT_ANALYST = 5
# AUDIT_ADMINISTRATOR = 6

AUDIT_CENTRE_LEAD_CLINICIAN = 1
AUDIT_CENTRE_CLINICIAN = 2
AUDIT_CENTRE_ADMINISTRATOR = 3
RCPCH_AUDIT_LEAD = 4
RCPCH_AUDIT_ANALYST = 5
RCPCH_AUDIT_ADMINISTRATOR = 6
RCPCH_AUDIT_PATIENT_FAMILY = 7

ROLES = (
    (AUDIT_CENTRE_LEAD_CLINICIAN, 'Audit Centre Lead Clinician'),
    (AUDIT_CENTRE_CLINICIAN, 'Audit Centre Clinician'),
    (AUDIT_CENTRE_ADMINISTRATOR, 'Audit Centre Administrator'),
    (RCPCH_AUDIT_LEAD, 'RCPCH Audit Lead'),
    (RCPCH_AUDIT_ANALYST, 'RCPCH Audit Analyst'),
    (RCPCH_AUDIT_ADMINISTRATOR, 'RCPCH Audit Administrator'),
    (RCPCH_AUDIT_PATIENT_FAMILY, 'RCPCH Audit Children and Family'),
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

# Case
CAN_VIEW_CHILD_NHS_NUMBER = (
    'can_view_child_nhs_number', 'Can view a child\'s NHS Number')
CAN_VIEW_CHILD_DATE_OF_BIRTH = (
    'can_view_child_date_of_birth', 'Can view a child\'s date of birth')
CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING = ('can_lock_child_case_data_from_editing',
                                         'Can lock a child\'s record from editing.')
CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING = ('can_unlock_child_case_data_from_editing',
                                           'Can unlock a child\'s record from editing.')
CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT = ('can_opt_out_child_from_inclusion_in_audit',
                                             'Can sanction an opt out from participating in the audit. Note all the child\'s date except Epilepsy12 unique identifier are irretrievably deleted.')
CAN_ONLY_VIEW_CHILD_CASE_DATA = ('can_only_view_child_case_data',
                                 'Can only view a child\'s demographic and case information.')

# Registration
CAN_APPROVE_ELIGIBILITY = ('can_approve_eligibility',
                           'Can approve eligibility for Epilepsy12.')
CAN_REMOVE_APPROVAL_OF_ELIGIBILITY = ('can_remove_approval_of_eligibility',
                                      'Can remove approval of eligibiltiy for Epilepsy12.')

CAN_REGISTER_CHILD_IN_EPILEPSY12 = ('can_register_child_in_epilepsy12',
                                    'Can register child in Epilepsy12. (A cohort number is automatically allocaeted)')
CAN_UNREGISTER_CHILD_IN_EPILEPSY12 = ('can_unregister_child_in_epilepsy12',
                                      'Can unregister a child in Epilepsy. Their record and previously entered data is untouched.')

CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE = ('can_only_view_general_paediatric_centre',
                                           'Can only view general paediatric centre.')
CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE = ('can_allocate_general_paediatric_centre',
                                          'Can allocate general paediatric centre.')
CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE = ('can_update_general_paediatric_centre',
                                        'Can edit or update but not delete general paediatric centre.')
CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE = ('can_delete_general_paediatric_centre',
                                        'Can delete general paediatric centre.')
CAN_ONLY_VIEW_TERTIARY_NEUROLOGY_CENTRE = ('can_only_view_tertiary_neurology_centre',
                                           'Can only view tertiary neurology centre.')
CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE = ('can_allocate_tertiary_neurology_centre',
                                          'Can allocate tertiary neurology centre.')
CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE = ('can_edit_tertiary_neurology_centre',
                                      'Can edit or update but not delete tertiary neurology centre.')
CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE = ('can_delete_tertiary_neurology_centre',
                                        'Can delete tertiary neurology centre.')
CAN_ONLY_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE = ('can_only_view_childrens_epilepsy_surgery_centre',
                                                   'Can only view children\'s epilepsy surgery centre.')
CAN_CONFIRM_CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET = ('can_confirm_childrens_epilepsy_surgical_service_referral_criteria_met',
                                                                         'Can confirm children\'s epilepsy surgery centre referral criteria have been met.')
CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE = ('can_allocate_childrens_epilepsy_surgery_centre',
                                                  'Can allocate children\'s epilepsy surgery centre.')
CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE = ('can_edit_childrens_epilepsy_surgery_centre',
                                              'Can edit or update but not delete children\'s epilepsy surgery centre.')
CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE = ('can_delete_childrens_epilepsy_surgery_centre',
                                                'Can delete children\'s epilepsy surgery centre.')
CAN_CONSENT_TO_AUDIT_PARTICIPATION = ('can_consent_to_audit_participation',
                                      'Can consent to participating in Epilepsy12.')

PERMISSIONS = (
    CAN_VIEW_CHILD_NHS_NUMBER,
    CAN_VIEW_CHILD_DATE_OF_BIRTH,
    CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
    CAN_ONLY_VIEW_CHILD_CASE_DATA,
    CAN_APPROVE_ELIGIBILITY,
    CAN_REMOVE_APPROVAL_OF_ELIGIBILITY,
    CAN_REGISTER_CHILD_IN_EPILEPSY12,
    CAN_UNREGISTER_CHILD_IN_EPILEPSY12,

    CAN_ONLY_VIEW_GENERAL_PAEDIATRIC_CENTRE,
    CAN_ONLY_VIEW_TERTIARY_NEUROLOGY_CENTRE,
    CAN_ONLY_VIEW_CHILDRENS_EPILEPSY_SURGERY_CENTRE,

    CAN_ALLOCATE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_UPDATE_GENERAL_PAEDIATRIC_CENTRE,
    CAN_DELETE_GENERAL_PAEDIATRIC_CENTRE,

    CAN_ALLOCATE_TERTIARY_NEUROLOGY_CENTRE,
    CAN_EDIT_TERTIARY_NEUROLOGY_CENTRE,
    CAN_DELETE_TERTIARY_NEUROLOGY_CENTRE,

    CAN_CONFIRM_CHILDRENS_EPILEPSY_SURGICAL_SERVICE_REFERRAL_CRITERIA_MET,
    CAN_ALLOCATE_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_EDIT_CHILDRENS_EPILEPSY_SURGERY_CENTRE,
    CAN_DELETE_CHILDRENS_EPILEPSY_SURGERY_CENTRE,

)
