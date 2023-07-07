"""
Seeds E12 Users in test db once per session.
"""

# Standard imports
import pytest

# 3rd Party imports
from django.contrib.auth.models import Group

# E12 Imports
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_rcpch_audit_lead_data,
)
from epilepsy12.models import (
    Organisation,
)
from .E12UserFactory import E12UserFactory
from epilepsy12.constants.user_types import (
    RCPCH_AUDIT_LEAD,
)


@pytest.mark.django_db
@pytest.fixture(scope="session")
def seed_users_fixture(django_db_setup, django_db_blocker):
    users = [
        test_user_audit_centre_administrator_data,
        test_user_audit_centre_clinician_data,
        test_user_audit_centre_lead_clinician_data,
        test_user_rcpch_audit_lead_data,
    ]
    
    with django_db_blocker.unblock():
        
        # Don't repeat seed
        if not Organisation.objects.filter(ODSCode="RP401").exists():

            TEST_USER_ORGANISATION = Organisation.objects.get(
                ODSCode="RP401",
                ParentOrganisation_ODSCode="RP4",
            )
        
            is_staff = False
            is_rcpch_audit_team_member=False 

            # seed a user of each type at GOSH
            for user in users:
                
                # set RCPCH AUDIT TEAM MEMBER ATTRIBUTE
                if user.role == RCPCH_AUDIT_LEAD:
                    is_staff = True
                    is_rcpch_audit_team_member=True 
                
                E12UserFactory(
                    first_name=user.role_str,
                    is_staff=is_staff,
                    is_rcpch_audit_team_member=is_rcpch_audit_team_member,
                    role=user.role,
                    organisation_employer=TEST_USER_ORGANISATION,
                    groups=[
                        Group.objects.get(
                            name=user.group_name
                        )
                    ],
                )


