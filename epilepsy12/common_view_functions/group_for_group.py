# python
# django
from django.contrib.auth.models import Group

# rcpch
from epilepsy12.constants.user_types import (
    # groups
    AUDIT_CENTRE_ADMINISTRATOR,
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    RCPCH_AUDIT_TEAM,
    RCPCH_AUDIT_PATIENT_FAMILY,
    # permissions
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    PATIENT_ACCESS,
    # preferences in the view
    VIEW_PREFERENCES,
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

    elif role_key == RCPCH_AUDIT_TEAM:
        group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)

    elif role_key == RCPCH_AUDIT_PATIENT_FAMILY:
        group = Group.objects.get(name=PATIENT_ACCESS)
    else:
        # no group
        group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)

    return group
