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

## View Tests

### E12 Patients 

[] Assert an Audit Centre Administrator can view patients inside own organisation - response.status_code == 200
[] Assert an Audit Centre Administrator CANNOT view patients outside own organisation - response.status_code == 403

[] Assert an audit centre clinician can view patients inside own organisation - response.status_code == 200
[] Assert an audit centre clinician CANNOT view patients outside own organisation - response.status_code == 403

[] Assert an Audit Centre Lead Clinician can view patients inside own Trust - response.status_code == 200
[] Assert an Audit Centre Lead Clinician CANNOT view patients outside own Trust - response.status_code == 403

[] Assert an RCPCH Audit Lead can view patients within all organisations - response.status_code == 200

### E12 Patient Records

[] Assert an Audit Centre Administrator can view patient records inside own organisation - response.status_code == 200
[] Assert an Audit Centre Administrator CANNOT view patient records outside own organisation - response.status_code == 403

[] Assert an audit centre clinician can view patient records inside own organisation - response.status_code == 200
[] Assert an audit centre clinician CANNOT view patient records outside own organisation - response.status_code == 403

[] Assert an Audit Centre Lead Clinician can view patient records inside own Trust - response.status_code == 200
[] Assert an Audit Centre Lead Clinician CANNOT view patient records outside own Trust - response.status_code == 403

[] Assert an RCPCH Audit Lead can view patient records within all organisations - response.status_code == 200

"""

# python imports
import pytest
import factory
from dataclasses import dataclass

# django imports
from django.urls import reverse
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

# E12 imports
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_ADMINISTRATOR,
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    RCPCH_AUDIT_LEAD,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
)
from epilepsy12.models import Epilepsy12User, Organisation
from epilepsy12.view_folder.case_views import case_list


# set up constants
@dataclass
class TestUser:
    role: int
    group_name: str


test_user_audit_centre_administrator = TestUser(
    role=AUDIT_CENTRE_ADMINISTRATOR, group_name=TRUST_AUDIT_TEAM_EDIT_ACCESS
)

test_user_audit_centre_clinician = TestUser(
    role=AUDIT_CENTRE_CLINICIAN, group_name=TRUST_AUDIT_TEAM_EDIT_ACCESS
)

test_user_audit_centre_lead_clinician = TestUser(
    role=AUDIT_CENTRE_LEAD_CLINICIAN, group_name=TRUST_AUDIT_TEAM_FULL_ACCESS
)

test_user_rcpch_audit_lead = TestUser(
    role=RCPCH_AUDIT_LEAD, group_name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS
)


@pytest.mark.parametrize(
    "ROLE, GROUP_NAME",
    [
        (
            test_user_audit_centre_administrator.role,
            test_user_audit_centre_administrator.group_name,
        ),
        (
            test_user_audit_centre_clinician.role,
            test_user_audit_centre_clinician.group_name,
        ),
        (
            test_user_audit_centre_lead_clinician.role,
            test_user_audit_centre_lead_clinician.group_name,
        ),
        (
            test_user_rcpch_audit_lead.role,
            test_user_rcpch_audit_lead.group_name,
        ),
    ],
)
@pytest.mark.django_db
def test_users_list_view_permissions_success(
    client, e12_user_factory, seed_groups_fixture, ROLE, GROUP_NAME
):
    """
    # Simulating different E12Users with different roles attempting to access the Users list of their own Trust. Additionally, RCPCH Audit Leads can access all organisations.

    [] Assert an Audit Centre Administrator can view users inside own Trust - response.status_code == 200
    [] Assert an Audit Centre Clinician can view users inside own Trust - response.status_code == 200
    [] Assert an Audit Centre Lead Clinician can view users inside own Trust - response.status_code == 200
    [] Assert an RCPCH Audit Lead can view users inside own Trust - response.status_code == 200
    [] Assert an RCPCH Audit Lead can view users inside a different Trust - response.status_code == 200

    """

    # set up constants
    
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )

    # ADDENBROOKE'S
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    is_staff = False
    is_rcpch_audit_team_member = False

    if ROLE == test_user_rcpch_audit_lead.role:
        is_staff = True
        is_rcpch_audit_team_member = True

    # Create Test User with specified Group
    test_user = e12_user_factory(
        is_staff=is_staff,
        is_rcpch_audit_team_member=is_rcpch_audit_team_member,
        role=ROLE,
        organisation_employer=TEST_USER_ORGANISATION,
        groups=[Group.objects.get(name=GROUP_NAME)],
    )

    # Create 2 users in same TRUST
    e12_user_factory.create_batch(
        2,
        is_staff=False,
        is_rcpch_audit_team_member=False,
        role=AUDIT_CENTRE_CLINICIAN,
        organisation_employer=TEST_USER_ORGANISATION,
        groups=[Group.objects.get(name=GROUP_NAME)],
    )

    # Log in Test User
    client.force_login(test_user)

    # Request e12 user list endpoint url same Trust
    e12_user_list_response_same_organisation = client.get(
        reverse(
            "epilepsy12_user_list",
            kwargs={"organisation_id": TEST_USER_ORGANISATION.id},
        )
    )

    assert (
        e12_user_list_response_same_organisation.status_code == 200
    ), f"{test_user.role} (from {test_user.organisation_employer}) requested user list of {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {e12_user_list_response_same_organisation.status_code}"

    # Additional test to RCPCH AUDIT LEADs who should be able to view all children nationally
    if ROLE == test_user_rcpch_audit_lead.role:
        # Create 2 users in a different trust
        e12_user_factory.create_batch(
            2,
            is_staff=False,
            is_rcpch_audit_team_member=False,
            role=AUDIT_CENTRE_CLINICIAN,
            organisation_employer=DIFF_TRUST_DIFF_ORGANISATION,
            groups=[Group.objects.get(name=GROUP_NAME)],
        )

        # Request e12 user list endpoint url diff org
        e12_user_list_response_different_organisation = client.get(
            reverse(
                "epilepsy12_user_list",
                kwargs={"organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id},
            )
        )

        assert (
            e12_user_list_response_different_organisation.status_code == 200
        ), f"{test_user.role} (from {test_user.organisation_employer}) requested user list of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {e12_user_list_response_different_organisation.status_code}"



@pytest.mark.django_db
def test_users_list_view_permissions_forbidden(
    client, e12_user_factory, seed_groups_fixture
):
    """
    # E12 Users

    [] Assert an Audit Centre Administrator CANNOT view users outside own organisation - response.status_code == 403
    [] Assert an audit centre clinician CANNOT view users outside own organisation - response.status_code == 403
    [] Assert an Audit Centre Lead Clinician CANNOT view users outside own Trust - response.status_code == 403
    """
    pass

@pytest.mark.django_db
def test_audit_centre_clinician_cases_list_access(
    client, e12_user_factory, seed_groups_fixture
):
    """Test to ensure Audit Centre Clinician (NOTE: NOT Lead Clinican) role can and can't view specified pages."""

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
        organisation_employer=ORGANISATION_TEST_USER,
        groups=[GROUP_AUDIT_CENTRE_CLINICIAN],
    )

    # log in user
    client.force_login(test_user)

    res_same_org = client.get(
        reverse("cases", kwargs={"organisation_id": ORGANISATION_TEST_USER.id})
    )

    assert (
        res_same_org.status_code == 200
    ), f"User from {ORGANISATION_TEST_USER} requesting cases list from {ORGANISATION_TEST_USER}. Expecting 200 status_code, receiving {res_same_org.status_code}"

    res_other_org = client.get(
        reverse("cases", kwargs={"organisation_id": ORGANISATION_OTHER.id})
    )

    assert (
        res_other_org.status_code == 403
    ), f"User from {ORGANISATION_TEST_USER} requesting cases list from {ORGANISATION_OTHER}. Expecting 403 status_code, receiving {res_other_org.status_code}"
