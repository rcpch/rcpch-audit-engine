"""
Tests the OrganisationEmployer   model
"""

# Standard imports
import pytest
from datetime import date

# Third party imports

# RCPCH imports
from epilepsy12.models import Epilepsy12User, Organisation
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_clinicial_audit_team_data,
    test_user_rcpch_audit_team_data,
)


@pytest.mark.django_db
def test_users_can_change_employer(seed_groups_fixture, seed_users_fixture):
    # Test that a user can change their employer

    ADDENBROOKES = Organisation.objects.get(ods_code="RGT01")  # Addenbrookes
    GOSH = Organisation.objects.get(ods_code="RP401")

    user_first_names_for_test = [
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)
    test_user = users.first()

    assert test_user.organisation_employer == GOSH

    test_user.set_organisation_employer(ADDENBROOKES)
    assert test_user.organisation_employer == ADDENBROOKES
    assert test_user.employer_organisations.count() == 2
    assert test_user.employer_organisations.filter(is_primary=True).count() == 1
