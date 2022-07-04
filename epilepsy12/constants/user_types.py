from django.utils.translation import gettext_lazy as _
from django.db import models


class Epilepsy12UserGroup(models.TextChoices):
    LEAD_CLINICIAN = 'lead_clinician', _("Lead Clinician")
    CLINICIAN = 'clinician', _("Clinician (not lead)"),
    CENTRE_ADMINISTRATOR = 'centre_admin', _("Centre Administrator")
    AUDIT_LEAD_ADMINISTRATOR = 'audit_lead_admin', _(
        "Audit Lead Administrator")
    AUDIT_ADMINISTRATOR = 'audit_admin', _("Audit Administrator (not lead)")
    AUDIT_ANALYST = 'audit_analyst', _("Audit Analyst")
    PATIENT = 'patient', _("Patient")
    PARENT = 'parent', _("Parent")


GROUPS = (
    Epilepsy12UserGroup.LEAD_CLINICIAN,
    Epilepsy12UserGroup.CLINICIAN,
    Epilepsy12UserGroup.CENTRE_ADMINISTRATOR,
    Epilepsy12UserGroup.AUDIT_LEAD_ADMINISTRATOR,
    Epilepsy12UserGroup.AUDIT_ADMINISTRATOR,
    Epilepsy12UserGroup.AUDIT_ANALYST,
    Epilepsy12UserGroup.PARENT,
    Epilepsy12UserGroup.PATIENT
)

PERMISSIONS = (
    # Case model
    ("can_create_case_named_centre", "Add Children to Epilepsy12 in named centre"),
    ("can_update_case_named_centre",
     "Edit Children's details in Epilepsy12 in named centre"),
    ("can_delete_case_named_centre",
     "Delete Children's details from Epilepsy12 in named centre"),
    ("can_view_case_named_centre",
     "View Children's details from Epilepsy12 in named centre"),
    ("can_lock_case_named_centre",
     "Lock Children's details from editing in Epilepsy12 in named centre"),
    ("can_create_case_all_centres", "Add Children to Epilepsy12 across all centres"),
    ("can_update_case_all_centres",
     "Edit Children's details in Epilepsy12 across all centres"),
    ("can_delete_case_all_centres",
     "Delete Children's details from Epilepsy12 across all centres"),
    ("can_view_case_all_centres",
     "View Children's details from Epilepsy12 across all centres"),
    ("can_lock_case_all_centres",
     "Lock Children's details from editing in Epilepsy12 across all centres"),
    # Registration model
    ("can_register_case_named_centre",
     "Register Children in an Epilepsy12 Cohort in a named centre"),
    ("can_delete_registration_named_centre",
     "Delete Children's registration from an Epilepsy12 Cohort in a named centre"),
    ("can_register_case_all_centres",
     "Register Children in an Epilepsy12 Cohort in any centre"),
    ("can_delete_registration_all_centres",
     "Delete Children's registration from an Epilepsy12 Cohor in any centret"),
    #  personal approval
    ('can_consent_to_audit_participation', "Consent to registration in Epilepsy12"),
    ('can_approve_audit_data_submission',
     "Provides final approval for data submission to Epilepsy12"),
    # Epilepsy12 audit data items
    ("can_view_named_centre_audit_items",
     "View Children's Epilepsy12 audit data items in named Centre"),
    ("can_edit_named_centre_audit_items",
     "Edit Children's Epilepsy12 audit data items in named Centre"),
    ("can_delete_named_centre_audit_items",
     "Delete Children's Epilepsy12 audit data items in named Centre"),
    ("can_create_named_centre_audit_items",
     "Add new audit data items to Epilepsy12 in named Centre"),
    ("can_view_all_centre_audit_items",
     "View Children's Epilepsy12 audit data items across all centres"),
    ("can_edit_all_centre_audit_items",
     "Edit Children's Epilepsy12 audit data items across all centres"),
    ("can_delete_all_centre_audit_items",
     "Delete Children's Epilepsy12 audit data items across all centres"),
    ("can_create_all_centre_audit_items",
     "Add new audit data items to Epilepsy12 across all centres"),
    # Centre Administration
    ("can_allocate_named_centre", "Allocate children to a named centre(s)"),
    ("can_allocate_all_centres", "Allocate children across all centres"),
    # User and Role Administration
    ("can_view_users_in_named_centres",
     "View all Epilepsy12 staff in named centres"),
    ("can_view_users_in_all_centres",
     "View all Epilepsy12 staff in all centres"),
    ("can_create_new_user_in_named_centres",
     "Add new Epilepsy12 staff in named centres"),
    ("can_create_new_user_in_all_centres",
     "Add new Epilepsy12 staff across all centres"),
    ("can_delete_user_in_named_centres",
     "Delete Epilepsy12 staff in named centres"),
    ("can_delete_user_in_all_centres",
     "Delete Epilepsy12 staff across all centres"),
    ("can_update_user_in_named_centres",
     "Edit Epilepsy12 staff details in named centres"),
    ("can_update_user_in_all_centres",
     "Edit Epilepsy12 staff details across all centres"),
    ("can_update_role_in_named_centres",
     "Edit Epilepsy12 staff roles in named centres"),
    ("can_update_role_in_all_centres",
     "Edit Epilepsy12 staff roles across all centres"),
    ("can_create_new_role_in_named_centres",
     "Create Epilepsy12 staff roles in named centres"),
    ("can_create_new_role_in_all_centres",
     "Create Epilepsy12 staff roles across all centres"),
    # superadmin access
    ("can_create_new_centre", "Create new Epilepsy12 centres"),
    ("can_delete_centre", "Delete Epilepsy12 centres"),
    ("can_update_centre", "Edit Epilepsy12 centre details"),
    ("can_create_roles", "Create new roles"),
    ("can_update_roles", "Edit roles"),
    ("can_delete_roles", "Delete roles"),
    ("can_view_permissions", "View permissions"),
    ("can_edit_permissions", "Edit permissions"),
    ("can_delete_permissions", "Delete permissions"),
    ("can_allocate_permissions", "Allocate permissions"),
    ("can_create_groups", "Create groups"),
    ("can_view_groups", "View groups"),
    ("can_update_groups", "Edit groups"),
    ("can_delete_groups", "Delete groups"),
    ("can_view_keywords", "View keywords"),
    ("can_create_keywords", "Create new keywords"),
    ("can_update_keywords", "Edit keywords"),
    ("can_delete_keywords", "Delete keywords"),
    ("can_view_hospitals", "View hospitals"),
    ("can_create_hospitals", "Create new hospitals"),
    ("can_update_hospitals", "Edit hospitals"),
    ("can_delete_hospitals", "Delete hospitals"),
    ("can_download_data_tables", "Download data tables")
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
