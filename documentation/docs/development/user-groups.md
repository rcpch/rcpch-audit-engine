---
title: User groups and permissions
reviewers: Dr Simon Chapman
---

The user groups are summarised [here](../clinician-users/clinician-user-guide.md###Permission)

Django allows permission-based and group based access. The user groups defined above are containers for permissions to all the models. Generic django permissions allow prescription of view, change, create and delete to each model (found in ```epilepsy12/constants/user_types.py```).

```python
# logged in user can view all national data but not logs
EPILEPSY12_AUDIT_TEAM_VIEW_ONLY = "epilepsy12_audit_team_view_only"

# logged in user can edit but not delete national data. Cannot view or edit logs or permissions.
EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS = "epilepsy12_audit_team_edit_access"

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
```

In addition, certain custom permissions associated with some models have been created:

```python
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
```

These permissions can be access in the view or in the template to constrain access to particular fields, views or models.

## Logging

A security requirement was the ability to track user activity. This is done in a number of ways.

### Login signpost

```python
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f'{user} ({user.email}) logged in from {get_client_ip(request)}.')
    VisitActivity.objects.create(
        activity=1,
        ip_address=get_client_ip(request),
        epilepsy12user=user
```

This picks up a successful login and reports this back in the template and stores the time and IP address. This code is taken from ```signals.py```.

### User logging

This pulls the same login and logout data from the ```VisitActivity``` and reports it in a table, accessible from the user table, depending on level of permission access.

### Audit trail

django-simple-history is a library dependency that creates a history model for each model, prepended by 'history_'. It is possible then through the django admin interface to view all models and model fields and identify which users have touched them.