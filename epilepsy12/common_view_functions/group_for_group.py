# python
# django
from django.contrib.auth.models import Group

# rcpch
from epilepsy12.constants.user_types import (
    ROLES,
    TITLES,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    AUDIT_CENTRE_CLINICIAN,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    AUDIT_CENTRE_ADMINISTRATOR,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    RCPCH_AUDIT_LEAD,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    RCPCH_AUDIT_ANALYST,
    EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS,
    RCPCH_AUDIT_ADMINISTRATOR,
    EPILEPSY12_AUDIT_TEAM_VIEW_ONLY,
    RCPCH_AUDIT_PATIENT_FAMILY,
    PATIENT_ACCESS,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    AUDIT_CENTRE_MANAGER,
)


def group_for_role(role_key):
    """
    Returns group for a role key
    """
    """
    Allocate Groups - the groups already have permissions allocated
    """
    if role_key == AUDIT_CENTRE_LEAD_CLINICIAN:
        group = Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)
    elif role_key == AUDIT_CENTRE_CLINICIAN:
        group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
    elif role_key == AUDIT_CENTRE_ADMINISTRATOR:
        group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)
    elif role_key == AUDIT_CENTRE_MANAGER:
        group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)
    elif role_key == RCPCH_AUDIT_LEAD:
        group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)
    elif role_key == RCPCH_AUDIT_ANALYST:
        group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS)
    elif role_key == RCPCH_AUDIT_ADMINISTRATOR:
        group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_VIEW_ONLY)
    elif role_key == RCPCH_AUDIT_PATIENT_FAMILY:
        group = Group.objects.get(name=PATIENT_ACCESS)
    else:
        # no group
        group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)

    return group
