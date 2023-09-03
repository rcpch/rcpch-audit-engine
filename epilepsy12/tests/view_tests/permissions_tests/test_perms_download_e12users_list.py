# python imports
import pytest
from datetime import date
from http import HTTPStatus

# 3rd party imports
from django.urls import reverse

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


@pytest.mark.django_db
def test_download_button_access(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,
):
    """Only RCPCH team and superusers should be able to download full E12Users list."""

    users = Epilepsy12User.objects.all()

    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        trust__ods_code="RP4",
    )

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        # Request download button url
        response = client.get(
            reverse(
                "download_e12_users",
                kwargs={"organisation_id": TEST_USER_ORGANISATION.id},
            )
        )
        if test_user.first_name == test_user_rcpch_audit_team_data.role_str:
            assert (
                response["Content-Disposition"]
                == 'attachment; filename="epilepsy12users.csv"'
            )
        else:
            assert response.status_code == HTTPStatus.FORBIDDEN
