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


def merged_parent_list_for_user(epilepsy12_user, organisation_list=None):
    """
    Returns a merged list of Trusts and Local Health Boards that the user can access.
    Each item in the list is a dict with:
    - pk: primary key
    - name: parent name  
    - parent_type: 'trust' or 'local_health_board'
    - ods_code: ODS code
    
    Avoids N+1 queries by fetching all parents in two queries, then merging in Python.
    
    Args:
        epilepsy12_user: The user to get parents for
        organisation_list: Optional pre-filtered organisation queryset. If None, 
                          will call organisation_white_list_for_user()
    
    Returns:
        List of dicts sorted by name
    """
    Trust = apps.get_model("epilepsy12", "Trust")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    
    # Get organisation list if not provided
    if organisation_list is None:
        organisation_list = organisation_white_list_for_user(epilepsy12_user)
    
    # Get all trusts and LHBs that have organisations in the whitelist
    # Using values_list to avoid loading full objects we don't need
    trust_ids = organisation_list.filter(
        trust__isnull=False, 
        active=True
    ).values_list('trust', flat=True).distinct()
    
    lhb_ids = organisation_list.filter(
        local_health_board__isnull=False, 
    ).values_list('local_health_board', flat=True).distinct()
    
    # Fetch all trusts and LHBs in two queries (not N+1)
    trusts = Trust.objects.filter(
        id__in=trust_ids,
        active=True
    ).values('pk', 'name', 'ods_code').order_by('name')
    
    lhbs = LocalHealthBoard.objects.filter(
        id__in=lhb_ids
    ).values('pk', 'name', 'ods_code').order_by('name')
    
    # Merge and annotate with parent_type
    merged_list = []
    
    for trust in trusts:
        merged_list.append({
            'pk': trust['pk'],
            'name': trust['name'],
            'parent_type': 'trust',
            'ods_code': trust['ods_code'],
        })
    
    for lhb in lhbs:
        merged_list.append({
            'pk': lhb['pk'],
            'name': lhb['name'],
            'parent_type': 'local_health_board',
            'ods_code': lhb['ods_code'],
        })
    
    # Sort by name
    merged_list.sort(key=lambda x: x['name'])
    
    return merged_list