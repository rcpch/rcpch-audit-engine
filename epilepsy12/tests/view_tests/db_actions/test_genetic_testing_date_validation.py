from datetime import date, timedelta

import pytest
from django.urls import reverse

from epilepsy12.models import Epilepsy12User, Organisation
from epilepsy12.tests.UserDataClasses import test_user_rcpch_audit_team_data
from epilepsy12.tests.factories import E12CaseFactory
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


@pytest.mark.django_db
@pytest.mark.parametrize("test_name", ["r14", "r27", "r59"])
def test_genetic_requested_date_after_achieved_is_rejected(
    client, seed_groups_fixture, seed_users_fixture, test_name
):
    test_user_organisation = Organisation.objects.get(
        ods_code="RP401", trust__ods_code="RP4"
    )
    case = E12CaseFactory.create(
        first_name=f"child_{test_user_organisation.name}",
        organisations__organisation=test_user_organisation,
        registration__investigations__genome_sequencing_requested=True,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)
    twofactor_signin(client, test_user)

    investigations = case.registration.investigations
    requested_field_name = f"{test_name}_test_requested_date"
    achieved_field_name = f"{test_name}_test_achieved_date"
    status_field_name = f"{test_name}_test_status"

    requested_date = date(2024, 1, 10)
    achieved_date = date(2024, 1, 20)
    setattr(investigations, status_field_name, "A")
    setattr(investigations, requested_field_name, requested_date)
    setattr(investigations, achieved_field_name, achieved_date)
    investigations.save()

    invalid_requested_date = achieved_date + timedelta(days=1)

    response = client.post(
        reverse(
            "genetic_testing_date_callback",
            kwargs={
                "investigations_id": investigations.id,
                "test_name": test_name,
                "requested_or_achieved": "requested",
            },
        ),
        headers={
            "Hx-Trigger-Name": requested_field_name,
            "Hx-Request": "true",
        },
        data={requested_field_name: invalid_requested_date.isoformat()},
    )

    investigations.refresh_from_db()

    assert getattr(investigations, requested_field_name) == requested_date
    assert isinstance(response.context["error_message"], ValueError)


@pytest.mark.django_db
@pytest.mark.parametrize("test_name", ["r14", "r27", "r59"])
def test_genetic_achieved_date_after_requested_is_accepted(
    client, seed_groups_fixture, seed_users_fixture, test_name
):
    test_user_organisation = Organisation.objects.get(
        ods_code="RP401", trust__ods_code="RP4"
    )
    case = E12CaseFactory.create(
        first_name=f"child_{test_user_organisation.name}",
        organisations__organisation=test_user_organisation,
        registration__investigations__genome_sequencing_requested=True,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)
    twofactor_signin(client, test_user)

    investigations = case.registration.investigations
    requested_field_name = f"{test_name}_test_requested_date"
    achieved_field_name = f"{test_name}_test_achieved_date"
    status_field_name = f"{test_name}_test_status"

    requested_date = date(2024, 1, 10)
    original_achieved_date = date(2024, 1, 15)
    valid_achieved_date = requested_date + timedelta(days=1)

    setattr(investigations, status_field_name, "A")
    setattr(investigations, requested_field_name, requested_date)
    setattr(investigations, achieved_field_name, original_achieved_date)
    investigations.save()

    response = client.post(
        reverse(
            "genetic_testing_date_callback",
            kwargs={
                "investigations_id": investigations.id,
                "test_name": test_name,
                "requested_or_achieved": "achieved",
            },
        ),
        headers={
            "Hx-Trigger-Name": achieved_field_name,
            "Hx-Request": "true",
        },
        data={achieved_field_name: valid_achieved_date.isoformat()},
    )

    investigations.refresh_from_db()

    assert getattr(investigations, achieved_field_name) == valid_achieved_date
    assert response.context["error_message"] is None


@pytest.mark.django_db
def test_genetic_date_callback_rejects_invalid_date_type(
    client, seed_groups_fixture, seed_users_fixture
):
    test_user_organisation = Organisation.objects.get(
        ods_code="RP401", trust__ods_code="RP4"
    )
    case = E12CaseFactory.create(
        first_name=f"child_{test_user_organisation.name}",
        organisations__organisation=test_user_organisation,
        registration__investigations__genome_sequencing_requested=True,
    )

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)
    twofactor_signin(client, test_user)

    investigations = case.registration.investigations
    investigations.r14_test_status = "A"
    investigations.r14_test_requested_date = date(2024, 1, 10)
    investigations.r14_test_achieved_date = date(2024, 1, 20)
    investigations.save()

    response = client.post(
        reverse(
            "genetic_testing_date_callback",
            kwargs={
                "investigations_id": investigations.id,
                "test_name": "r14",
                "requested_or_achieved": "invalid-date-type",
            },
        ),
        headers={
            "Hx-Trigger-Name": "r14_test_requested_date",
            "Hx-Request": "true",
        },
        data={"r14_test_requested_date": date(2024, 1, 11).isoformat()},
    )

    investigations.refresh_from_db()

    assert investigations.r14_test_requested_date == date(2024, 1, 10)
    assert investigations.r14_test_achieved_date == date(2024, 1, 20)
    assert isinstance(response.context["error_message"], ValueError)
    assert "Invalid date type" in str(response.context["error_message"])
