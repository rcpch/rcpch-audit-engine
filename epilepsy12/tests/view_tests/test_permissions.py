"""
Tests to ensure permissions work as expected.



NOTE: if you wish to quickly seed test users inside the shell, use this code:

from django.contrib.auth.models import Group
# E12 imports
from epilepsy12.constants.user_types import (
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    AUDIT_CENTRE_CLINICIAN,
)
from epilepsy12.models import Organisation
from epilepsy12.tests.factories import E12UserFactory

GROUP_AUDIT_CENTRE_CLINICIAN = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
ORGANISATION_TEST_USER = Organisation.objects.get(ODSCode="RP401")
ORGANISATION_OTHER = Organisation.objects.get(ODSCode="RGT01")

# Create Test User with specified Group
E12UserFactory(
    is_staff=False,
    is_rcpch_audit_team_member=False,
    is_superuser=False,
    role=AUDIT_CENTRE_CLINICIAN,
    organisation_employer = ORGANISATION_TEST_USER,
    groups=[GROUP_AUDIT_CENTRE_CLINICIAN],
)

# Test Cases

## Scope Tests

[] Assert an audit centre clinician can only view patients from own organisation
[] Assert an Audit Centre Administrator can only view patients from own organisation
[] Assert an Audit Centre Lead Clinician can only view patients from own Trust
[] Assert an RCPCH Audit Lead can view all patients

[] Assert an audit centre clinician can only view users from own organisation
[] Assert an Audit Centre Administrator can only view users from own organisation
[] Assert an Audit Centre Lead Clinician can only view users from own Trust
[] Assert an RCPCH Audit Lead can view all users

[] Assert an audit centre clinician can only view patient records from own organisation
[] Assert an Audit Centre Administrator can only view patient records from own organisation
[] Assert an Audit Centre Lead Clinician can only view patient records from own Trust
[] Assert an RCPCH Audit Lead can view all patient records
"""

# python imports
import pytest
import factory

# django imports
from django.urls import reverse
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

# E12 imports
from epilepsy12.constants.user_types import (
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    AUDIT_CENTRE_CLINICIAN,
)
from epilepsy12.models import Epilepsy12User, Organisation
from epilepsy12.view_folder.case_views import case_list


@pytest.mark.django_db
def test_audit_centre_clinician(client, e12_user_factory, seed_groups_fixture):
    """Test to ensure Audit Centre Clinician (NOTE: NOT Lead Clinican) role can and can't view specified pages."""

    # set up constants
    AUDIT_CENTRE_CLINICIAN_GROUP = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
    TEST_USER_ORGANISATION = Organisation.objects.get(ODSCode="RP401")
    DIFFERENT_USER_ORGANISATION = Organisation.objects.get(ODSCode="RGT01")

    # Create Test User with specified Group
    test_user = e12_user_factory(
        is_staff=False,
        is_rcpch_audit_team_member=False,
        role=AUDIT_CENTRE_CLINICIAN,
        organisation_employer = TEST_USER_ORGANISATION,
        groups=[AUDIT_CENTRE_CLINICIAN_GROUP]
    )

    # Create another 2 users in the same Organisation (GOSH is default)
    batch = e12_user_factory.create_batch(
        2,
        is_staff=True,
        is_rcpch_audit_team_member=False,
        role=AUDIT_CENTRE_CLINICIAN,
        organisation_employer = TEST_USER_ORGANISATION,
        groups=[AUDIT_CENTRE_CLINICIAN_GROUP]
    )
    
    # Create another 2 users in a DIFFERENT Organisation
    batch = e12_user_factory.create_batch(
        2,
        is_staff=True,
        is_rcpch_audit_team_member=False,
        role=AUDIT_CENTRE_CLINICIAN,
        organisation_employer=DIFFERENT_USER_ORGANISATION,
        groups=[AUDIT_CENTRE_CLINICIAN_GROUP],
    )
    
    
    # Log in Test User
    client.force_login(test_user)
    
    # assert that user CAN view the 2 users in same organisation but NOT the 2 users in a different organisation
    
    response_same_org = client.get(f'/organisation/{TEST_USER_ORGANISATION.id}/epilepsy12_user_list/')
    response_diff_org = client.get(f'/organisation/{DIFFERENT_USER_ORGANISATION.id}/epilepsy12_user_list/')
    
    assert response_same_org.status_code == 200, f"User from {TEST_USER_ORGANISATION} requested to see Users list from their own organisation, but not receiving 200 response"
    
    assert response_diff_org.status_code == 403, f"User from {TEST_USER_ORGANISATION} requested to see Users list from different organisation ({DIFFERENT_USER_ORGANISATION}). Expecting 403, receiving {response_diff_org.status_code}"



@pytest.mark.django_db
def test_audit_centre_clinician_cases_list_access(client, e12_user_factory, seed_groups_fixture):
    """Test to ensure Audit Centre Clinician (NOTE: NOT Lead Clinican) role can and can't view specified pages.
    
    """
    
     # set up constants
    GROUP_AUDIT_CENTRE_CLINICIAN = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
    ORGANISATION_TEST_USER = Organisation.objects.get(ODSCode="RP401")
    ORGANISATION_OTHER = Organisation.objects.get(ODSCode="RGT01")

    # Create Test User with specified Group
    test_user = e12_user_factory(
        is_staff=False,
        is_rcpch_audit_team_member=False,
        is_superuser=False,
        role=AUDIT_CENTRE_CLINICIAN,
        organisation_employer = ORGANISATION_TEST_USER,
        groups=[GROUP_AUDIT_CENTRE_CLINICIAN],
    )
    
    # log in user
    client.force_login(test_user)
    
    res_same_org = client.get(reverse('cases', kwargs={'organisation_id':ORGANISATION_TEST_USER.id}))
    
    
    assert res_same_org.status_code == 200, f"User from {ORGANISATION_TEST_USER} requesting cases list from {ORGANISATION_TEST_USER}. Expecting 200 status_code, receiving {res_same_org.status_code}"

    res_other_org = client.get(reverse('cases', kwargs={'organisation_id':ORGANISATION_OTHER.id}))  
    

    assert res_other_org.status_code == 403, f"User from {ORGANISATION_TEST_USER} requesting cases list from {ORGANISATION_OTHER}. Expecting 403 status_code, receiving {res_other_org.status_code}"
    