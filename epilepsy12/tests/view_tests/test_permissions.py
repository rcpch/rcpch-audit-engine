"""
Tests to ensure permissions work as expected.
"""

# python imports
import pytest
import factory

# django imports
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# E12 imports
from epilepsy12.constants.user_types import (
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    AUDIT_CENTRE_CLINICIAN,
)
from epilepsy12.models import Epilepsy12User, Organisation


@pytest.mark.django_db
def test_audit_centre_clinician(client, e12_user_factory, seed_groups_fixture):
    """Test to ensure Audit Centre Clinician (NOTE: NOT Lead Clinican) role can and can't view specified pages."""

    # set up constants
    AUDIT_CENTRE_CLINICIAN_GROUP = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
    TEST_USER_ORGANISATION = Organisation.objects.get(ODSCode="RP401")
    DIFFERENT_USER_ORGANISATION = Organisation.objects.get(ODSCode="RGT01")

    # Create Test User with specified Group
    test_user = e12_user_factory(
        is_staff=True,
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
    
    assert response_diff_org.status_code == 403, f"User from {TEST_USER_ORGANISATION} requested to see Users list from different organisation ({DIFFERENT_USER_ORGANISATION}), but not receiving 403 response"

