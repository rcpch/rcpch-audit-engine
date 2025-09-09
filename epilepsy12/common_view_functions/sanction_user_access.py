from django.apps import apps
from django.db.models import Q


def logged_in_user_may_access_this_organisation(user, organisation_requested):
    """
    Called from selected_trust_kpis
    Ensures only trusted users can run aggregations or publish results for that organisation
    """
    if (user.is_active and user.email_confirmed) or user.is_superuser:
        if user.is_rcpch_audit_team_member or user.is_rcpch_staff or user.is_superuser:
            # RCPCH staff or E12 RCPCH staff can see all children across the UK
            return True
        else:
            # regular user - not a member of RCPCH
            if user.organisation_employer.trust == organisation_requested.trust:
                # user's employing trust is the same as the trust of the organisation requested
                return True
            else:
                False

    else:
        # user is not active or email confirmed
        return False


def organisation_white_list_for_user(epilepsy12_user):
    """
    Returns a list of organisations that the user can access.
    """
    Organisation = apps.get_model("epilepsy12", "Organisation")
    return (
        Organisation.objects.filter(
            Q(
                trust__in=Organisation.objects.filter(
                    epilepsy12_users__epilepsy12_user=epilepsy12_user,
                    epilepsy12_users__is_active=True,
                    trust__isnull=False,
                )
                .values_list("trust", flat=True)
                .distinct()
            )
            | Q(
                local_health_board__in=Organisation.objects.filter(
                    epilepsy12_users__epilepsy12_user=epilepsy12_user,
                    epilepsy12_users__is_active=True,
                    local_health_board__isnull=False,
                )
                .values_list("local_health_board", flat=True)
                .distinct()
            )
        )
        .filter(active=True)
        .distinct()
        .order_by("name")
    )
