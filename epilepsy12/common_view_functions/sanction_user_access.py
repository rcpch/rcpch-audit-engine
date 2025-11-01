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
    - country: country code (for trusts only)
    
    Avoids N+1 queries by fetching all parents in two queries, then merging in Python.
    
    Special handling for Jersey:
    - Jersey is a special case (country="Jersey") with its own trust
    - Jersey users can only see Jersey trust
    - Non-Jersey users cannot see Jersey trust unless employed there
    - Admin users can see all trusts including Jersey
    
    Args:
        epilepsy12_user: The user to get parents for
        organisation_list: Optional pre-filtered organisation queryset. If None, 
                          will call organisation_white_list_for_user()
    
    Returns:
        List of dicts sorted by name
    """
    Trust = apps.get_model("epilepsy12", "Trust")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    Organisation = apps.get_model("epilepsy12", "Organisation")
    
    # Get organisation list if not provided
    if organisation_list is None:
        organisation_list = organisation_white_list_for_user(epilepsy12_user)
    
    # Check if user is admin (can see all trusts including Jersey)
    is_admin = (
        epilepsy12_user.is_rcpch_staff or 
        epilepsy12_user.is_superuser or 
        epilepsy12_user.is_rcpch_audit_team_member
    )
    
    # Check if user is employed at Jersey (only do this check for non-admin users)
    # Jersey country can be "Jersey" or "JERSEY" (case-insensitive check)
    if not is_admin:
        user_organisations = Organisation.objects.filter(
            epilepsy12_users__epilepsy12_user=epilepsy12_user,
            epilepsy12_users__is_active=True,
        )
        user_is_jersey_employed = user_organisations.filter(
            trust__country__iexact="JERSEY"
        ).exists()
    else:
        # Admin users can see everything, so we don't need to check Jersey employment
        user_is_jersey_employed = True  # Set to True so Jersey is not filtered out
    
    # Get all trusts and LHBs that have organisations in the whitelist
    # Using values_list to avoid loading full objects we don't need
    # organisation_list is already filtered by active=True organisations
    trust_ids = organisation_list.filter(
        trust__isnull=False
    ).values_list('trust', flat=True).distinct()
    
    lhb_ids = organisation_list.filter(
        local_health_board__isnull=False
    ).values_list('local_health_board', flat=True).distinct()
    
    # Fetch all trusts and LHBs in two queries (not N+1)
    # Only trusts have an active field - LHBs don't
    # Include country field for Jersey filtering
    trusts = Trust.objects.filter(
        id__in=trust_ids,
        active=True
    ).values('pk', 'name', 'ods_code', 'country').order_by('name')
    
    lhbs = LocalHealthBoard.objects.filter(
        id__in=lhb_ids
    ).values('pk', 'name', 'ods_code').order_by('name')
    
    # Merge and annotate with parent_type
    # Filter out Jersey for non-Jersey users (unless they're employed there)
    merged_list = []
    
    for trust in trusts:
        # Skip Jersey trust if user is not employed there
        # Jersey country can be "Jersey" or "JERSEY" - case insensitive check
        if trust['country'] and trust['country'].upper() == 'JERSEY' and not user_is_jersey_employed:
            continue
            
        merged_list.append({
            'pk': trust['pk'],
            'name': trust['name'],
            'parent_type': 'trust',
            'ods_code': trust['ods_code'],
            'country': trust['country'],
        })
    
    for lhb in lhbs:
        merged_list.append({
            'pk': lhb['pk'],
            'name': lhb['name'],
            'parent_type': 'local_health_board',
            'ods_code': lhb['ods_code'],
            'country': None,  # LHBs don't have country field
        })
    
    # Sort by name
    merged_list.sort(key=lambda x: x['name'])
    
    return merged_list