# LEAD_CLINICIAN = 1
# CENTRE_ADMINISTRATOR = 2
# PAEDIATRIC_NEUROLOGIST = 3
# GENERAL_PAEDIATRICIAN_WITH_EPILEPSY_INTEREST = 4
# AUDIT_ANALYST = 5
# AUDIT_ADMINISTRATOR = 6

VIEW_PREFERENCES = (
    (0, "organisation"),
    (1, "trust"),
    (2, "national"),
)

AUDIT_CENTRE_LEAD_CLINICIAN = 1
AUDIT_CENTRE_CLINICIAN = 2
AUDIT_CENTRE_ADMINISTRATOR = 3
RCPCH_AUDIT_TEAM = 4
RCPCH_AUDIT_PATIENT_FAMILY = 7

ROLES = (
    (AUDIT_CENTRE_LEAD_CLINICIAN, "Audit Centre Lead Clinician"),
    (AUDIT_CENTRE_CLINICIAN, "Audit Centre Clinician"),
    (AUDIT_CENTRE_ADMINISTRATOR, "Audit Centre Administrator"),
    (RCPCH_AUDIT_TEAM, "RCPCH Audit Team"),
    (RCPCH_AUDIT_PATIENT_FAMILY, "RCPCH Audit Children and Family"),
)

AUDIT_CENTRE_ROLES = (
    (AUDIT_CENTRE_LEAD_CLINICIAN, "Audit Centre Lead Clinician"),
    (AUDIT_CENTRE_CLINICIAN, "Audit Centre Clinician"),
    (AUDIT_CENTRE_ADMINISTRATOR, "Audit Centre Administrator"),
)

RCPCH_AUDIT_TEAM_ROLES = ((RCPCH_AUDIT_TEAM, "RCPCH Audit Team"),)

MR = 1
MRS = 2
MS = 3
DR = 4
PROFESSOR = 5

TITLES = ((MR, "Mr"), (MRS, "Mrs"), (MS, "Ms"), (DR, "Dr"), (PROFESSOR, "Professor"))

"""
Groups
"""
# logged in user access all areas: can create/update/delete any audit data, logs, epilepsy key words and organisation trusts, groups and permissions
EPILEPSY12_AUDIT_TEAM_FULL_ACCESS = "epilepsy12_audit_team_full_access"

# logged in user can view all data relating to their trust(s) but not logs
TRUST_AUDIT_TEAM_VIEW_ONLY = "trust_audit_team_view_only"

# logged in user can edit but not delete all data relating to their trust(s) but not view or edit logs, epilepsy key words and organisation trusts, groups and permissions
TRUST_AUDIT_TEAM_EDIT_ACCESS = "trust_audit_team_edit_access"

# logged in user can delete all data relating to their trust(s) but not view or edit logs, epilepsy key words and organisation trusts, groups and permissions
TRUST_AUDIT_TEAM_FULL_ACCESS = "trust_audit_team_full_access"

# logged in user can view their own audit data, consent to participation and remove that consent/opt out. Opting out would delete all data relating to them, except the epilepsy12 unique identifier
PATIENT_ACCESS = "patient_access"

GROUPS = (
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    PATIENT_ACCESS,
)

# Case
CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING = (
    "can_lock_child_case_data_from_editing",
    "Can lock a child's record from editing.",
)
CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING = (
    "can_unlock_child_case_data_from_editing",
    "Can unlock a child's record from editing.",
)
CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT = (
    "can_opt_out_child_from_inclusion_in_audit",
    "Can sanction an opt out from participating in the audit. Note all the child's date except Epilepsy12 unique identifier are irretrievably deleted.",
)

# Registration
CAN_APPROVE_ELIGIBILITY = (
    "can_approve_eligibility",
    "Can approve eligibility for Epilepsy12.",
)
CAN_REMOVE_APPROVAL_OF_ELIGIBILITY = (
    "can_remove_approval_of_eligibility",
    "Can remove approval of eligibiltiy for Epilepsy12.",
)

CAN_REGISTER_CHILD_IN_EPILEPSY12 = (
    "can_register_child_in_epilepsy12",
    "Can register child in Epilepsy12. (A cohort number is automatically allocaeted)",
)
CAN_UNREGISTER_CHILD_IN_EPILEPSY12 = (
    "can_unregister_child_in_epilepsy12",
    "Can unregister a child in Epilepsy. Their record and previously entered data is untouched.",
)

CAN_ALLOCATE_EPILEPSY12_LEAD_CENTRE = (
    "can_allocate_epilepsy12_lead_centre",
    "Can allocate this child to any Epilepsy12 centre.",
)

CAN_TRANSFER_EPILEPSY12_LEAD_CENTRE = (
    "can_transfer_epilepsy12_lead_centre",
    "Can transfer this child to another Epilepsy12 centre.",
)

CAN_EDIT_EPILEPSY12_LEAD_CENTRE = (
    "can_edit_epilepsy12_lead_centre",
    "Can edit this child's current Epilepsy12 lead centre.",
)

CAN_DELETE_EPILEPSY12_LEAD_CENTRE = (
    "can_delete_epilepsy12_lead_centre",
    "Can delete Epilepsy12 lead centre.",
)

CAN_CONSENT_TO_AUDIT_PARTICIPATION = (
    "can_consent_to_audit_participation",
    "Can consent to participating in Epilepsy12.",
)

PERMISSIONS = (
    CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
    CAN_APPROVE_ELIGIBILITY,
    CAN_REMOVE_APPROVAL_OF_ELIGIBILITY,
    CAN_REGISTER_CHILD_IN_EPILEPSY12,
    CAN_UNREGISTER_CHILD_IN_EPILEPSY12,
    CAN_EDIT_EPILEPSY12_LEAD_CENTRE,
    CAN_ALLOCATE_EPILEPSY12_LEAD_CENTRE,
    CAN_TRANSFER_EPILEPSY12_LEAD_CENTRE,
    CAN_DELETE_EPILEPSY12_LEAD_CENTRE,
    CAN_CONSENT_TO_AUDIT_PARTICIPATION,
)
