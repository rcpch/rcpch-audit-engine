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
    test_user_rcpch_audit_team_data,
    test_user_clinicial_audit_team_data,
)
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
)
from .E12UserFactory import E12UserFactory
from epilepsy12.constants.user_types import (
    RCPCH_AUDIT_TEAM,
)


@pytest.mark.django_db
@pytest.fixture(scope="session")
def seed_users_fixture(django_db_setup, django_db_blocker):
    users = [
        test_user_audit_centre_administrator_data,
        test_user_audit_centre_clinician_data,
        test_user_audit_centre_lead_clinician_data,
        test_user_rcpch_audit_team_data,
        test_user_clinicial_audit_team_data,
    ]

    with django_db_blocker.unblock():
        # Don't repeat seed
        if not Epilepsy12User.objects.exists():
            GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
            KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")
            NOAHS_ARK = Organisation.objects.get(ods_code="7A4H1", local_health_board__ods_code="7A4")

            for org in [GOSH, KINGS, NOAHS_ARK]:
                is_active = True
                is_staff = False
                is_rcpch_audit_team_member = False
                is_rcpch_staff = False

                # seed a user of each type
                for user in users:
                    first_name = user.role_str

                    # set RCPCH AUDIT TEAM MEMBER ATTRIBUTE
                    if user.role == RCPCH_AUDIT_TEAM:
                        is_rcpch_audit_team_member = True
                        is_rcpch_staff = True

                    if user.is_clinical_audit_team:
                        is_rcpch_audit_team_member = True
                        first_name = "CLINICAL_AUDIT_TEAM"

                    E12UserFactory(
                        first_name=first_name,
                        role=user.role,
                        # Assign flags based on user role
                        is_active=is_active,
                        is_staff=is_staff,
                        is_rcpch_audit_team_member=is_rcpch_audit_team_member,
                        is_rcpch_staff=is_rcpch_staff,
                        organisation_employer=org,
                        groups=[user.group_name],
                    )
        else:
            print("Test users already seeded. Skipping")
