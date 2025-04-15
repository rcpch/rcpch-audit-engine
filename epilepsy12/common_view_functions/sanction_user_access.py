from django.core.exceptions import PermissionDenied
from django.apps import apps


def logged_in_user_may_access_this_organisation(user, organisation_requested):
    """
    Called from selected_trust_kpis
    Ensures only trusted users can run aggregations or publish results for that organisation
    """
    if (user.is_active and user.email_confirmed) or user.is_superuser:
        if (
            user.is_rcpch_audit_team_member
            or user.is_rcpch_staff
            or user.is_superuser
        ):
            # RCPCH staff or E12 RCPCH staff can see all children across the UK
            return True
        else:
            # regular user - not a member of RCPCH
            if (
                user.organisation_employer.trust
                == organisation_requested.trust
            ):
                # user's employing trust is the same as the trust of the organisation requested
                return True
            else:
                False

    else:
        # user is not active or email confirmed
        return False
