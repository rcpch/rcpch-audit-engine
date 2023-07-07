"""
This file houses code to be copied and pasted easily into the Django Python shell.
"""



# Seeds test db users according to role + permissions.

from django.contrib.auth.models import Group
from epilepsy12.tests.UserDataClasses import test_user_audit_centre_administrator_data,        test_user_audit_centre_clinician_data,        test_user_audit_centre_lead_clinician_data,        test_user_rcpch_audit_team_data,        test_user_clinicial_audit_team_data

from epilepsy12.models import Organisation
from epilepsy12.tests.factories.E12UserFactory import E12UserFactory
from epilepsy12.constants.user_types import RCPCH_AUDIT_TEAM

users = [
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_rcpch_audit_team_data,
    test_user_clinicial_audit_team_data,
]

TEST_USER_ORGANISATION = Organisation.objects.get(
    ODSCode="RP401",
    ParentOrganisation_ODSCode="RP4",
)

E12UserFactory(
    first_name=test_user_audit_centre_administrator_data.role_str,
    role=test_user_audit_centre_administrator_data.role,
    # Assign flags based on user role
    is_active=True,
    is_staff=False,
    is_rcpch_audit_team_member=False,
    is_rcpch_staff=False,
    organisation_employer=TEST_USER_ORGANISATION,
    groups=[
        Group.objects.get(name=test_user_audit_centre_administrator_data.group_name)
    ],
)
