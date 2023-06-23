"""
## Delete Tests

    [x] Assert an Audit Centre Lead Clinician can delete users inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can delete users inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can delete users outside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can delete users inside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can delete users outside own Trust - HTTPStatus.OK

    [x] Assert an Audit Centre Administrator CANNOT delete users - HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT delete users - HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT delete users outside own Trust - HTTPStatus.FORBIDDEN
    
    

    [] Assert an Audit Centre Lead Clinician can delete patients inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can delete patients inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can delete patients outside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can delete patients inside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can delete patients outside own Trust - HTTPStatus.OK
    
    [] Assert an Audit Centre Administrator CANNOT delete patients - HTTPStatus.FORBIDDEN
    [] Assert an audit centre clinician CANNOT delete patients outside own Trust - HTTPStatus.FORBIDDEN
    [] Assert an Audit Centre Lead Clinician CANNOT delete patients outside own Trust - HTTPStatus.FORBIDDEN


# Episode

    [] Assert an Audit Centre Lead Clinician can 'remove_episode' inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can 'remove_episode' inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can 'remove_episode' outside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can 'remove_episode' inside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can 'remove_episode' outside own Trust - HTTPStatus.OK
    
    [] Assert an Audit Centre Administrator CANNOT  'remove_episode' - HTTPStatus.FORBIDDEN
    [] Assert an audit centre clinician CANNOT  'remove_episode' outside own Trust - HTTPStatus.FORBIDDEN
    [] Assert an Audit Centre Lead Clinician CANNOT  'remove_episode' outside own Trust - HTTPStatus.FORBIDDEN

# Syndrome

    [] Assert an Audit Centre Lead Clinician can 'remove_syndrome' inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can 'remove_syndrome' inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can 'remove_syndrome' outside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can 'remove_syndrome' inside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can 'remove_syndrome' outside own Trust - HTTPStatus.OK
    
    [] Assert an Audit Centre Administrator CANNOT  'remove_syndrome' - HTTPStatus.FORBIDDEN
    [] Assert an audit centre clinician CANNOT  'remove_syndrome' outside own Trust - HTTPStatus.FORBIDDEN
    [] Assert an Audit Centre Lead Clinician CANNOT  'remove_syndrome' outside own Trust - HTTPStatus.FORBIDDEN

# Comorbidity

    [] Assert an Audit Centre Lead Clinician can 'remove_comorbidity' inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can 'remove_comorbidity' inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can 'remove_comorbidity' outside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can 'remove_comorbidity' inside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can 'remove_comorbidity' outside own Trust - HTTPStatus.OK
    
    [] Assert an Audit Centre Administrator CANNOT  'remove_comorbidity' - HTTPStatus.FORBIDDEN
    [] Assert an audit centre clinician CANNOT  'remove_comorbidity' outside own Trust - HTTPStatus.FORBIDDEN
    [] Assert an Audit Centre Lead Clinician CANNOT  'remove_comorbidity' outside own Trust - HTTPStatus.FORBIDDEN
    

# Antiepilepsy Medicine

    [] Assert an Audit Centre Lead Clinician can 'remove_antiepilepsy_medicine' inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can 'remove_antiepilepsy_medicine' inside own Trust - HTTPStatus.OK
    [] Assert RCPCH Audit Team can 'remove_antiepilepsy_medicine' outside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can 'remove_antiepilepsy_medicine' inside own Trust - HTTPStatus.OK
    [] Assert Clinical Audit Team can 'remove_antiepilepsy_medicine' outside own Trust - HTTPStatus.OK
    
    [] Assert an Audit Centre Administrator CANNOT  'remove_antiepilepsy_medicine' - HTTPStatus.FORBIDDEN
    [] Assert an audit centre clinician CANNOT  'remove_antiepilepsy_medicine' outside own Trust - HTTPStatus.FORBIDDEN
    [] Assert an Audit Centre Lead Clinician CANNOT  'remove_antiepilepsy_medicine' outside own Trust - HTTPStatus.FORBIDDEN
"""

# python imports
import pytest
from http import HTTPStatus

# django imports
from django.urls import reverse

# E12 Imports
from epilepsy12.tests.factories import E12UserFactory, E12CaseFactory
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_clinicial_audit_team_data,
    test_user_rcpch_audit_team_data,
)
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    Case,
)
from epilepsy12.constants import VALID_NHS_NUMS


@pytest.mark.django_db
def test_user_delete_success(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,
):
    """Simulating different E12 users with different roles attempting to delete Users inside own trust.

    Additionally, RCPCH Audit Team and Clinical Audit Team roles should be able to delete user in different trust.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}"

    for test_user in users:
        client.force_login(test_user)

        # Seed a temp User to be deleted
        temp_user_same_org = E12UserFactory(
            first_name="temp_user",
            email=f"temp_{test_user.first_name}@temp.com",
            role=test_user.role,
            is_active=1,
            organisation_employer=TEST_USER_ORGANISATION,
            groups=[test_user_audit_centre_administrator_data.group_name],
        )

        url = reverse(
            "delete_epilepsy12_user",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "epilepsy12_user_id": temp_user_same_org.id,
            },
        )

        response = client.get(url)

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` for User from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected 200 response status code, received {response.status_code}"

        # Additional test for deleting users outside of own Trust
        if test_user.first_name in [
            test_user_clinicial_audit_team_data.role_str,
            test_user_rcpch_audit_team_data.role_str,
        ]:
            # Seed a temp User to be deleted
            temp_user_same_org = E12UserFactory(
                first_name="temp_user",
                email=f"temp_{test_user.first_name}@temp.com",
                role=test_user.role,
                is_active=1,
                organisation_employer=DIFF_TRUST_DIFF_ORGANISATION,
                groups=[test_user_audit_centre_administrator_data.group_name],
            )

            url = reverse(
                "delete_epilepsy12_user",
                kwargs={
                    "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                    "epilepsy12_user_id": temp_user_same_org.id,
                },
            )

            response = client.get(url)

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` for User from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected 200 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_user_delete_forbidden(
    client,
):
    """Simulating different E12 users with different roles attempting to delete Users inside own trust.

    Audit Centre Lead Clinician role CANNOT delete user in different trust.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    # Seed a temp User for attempt to delete
    temp_user_same_org = E12UserFactory(
        first_name="temp_user",
        email=f"temp_user_same_org@temp.com",
        role=test_user_audit_centre_administrator_data.role,
        is_active=1,
        organisation_employer=TEST_USER_ORGANISATION,
        groups=[test_user_audit_centre_administrator_data.group_name],
    )
    # Seed a temp User to be deleted
    temp_user_same_org = E12UserFactory(
        first_name="temp_user",
        email=f"temp_user_diff_org@temp.com",
        role=test_user_audit_centre_administrator_data.role,
        is_active=1,
        organisation_employer=DIFF_TRUST_DIFF_ORGANISATION,
        groups=[test_user_audit_centre_administrator_data.group_name],
    )

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}"

    for test_user in users:
        client.force_login(test_user)

        if test_user.first_name in [
            test_user_audit_centre_lead_clinician_data.role_str,
        ]:
            url = reverse(
                "delete_epilepsy12_user",
                kwargs={
                    "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                    "epilepsy12_user_id": temp_user_same_org.id,
                },
            )

            response = client.get(url)

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` for User from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"

        else:
            url = reverse(
                "delete_epilepsy12_user",
                kwargs={
                    "organisation_id": TEST_USER_ORGANISATION.id,
                    "epilepsy12_user_id": temp_user_same_org.id,
                },
            )

            response = client.get(url)

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` for User from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_patient_delete_success(
    client,
):
    """Simulating different E12 users with different roles attempting to delete Patients inside own trust.

    Additionally, RCPCH Audit Team and Clinical Audit Team roles should be able to delete patient in different trust.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}"

    for test_user in users:
        client.force_login(test_user)

        # Seed a temp pt to be deleted
        temp_pt_same_org = E12CaseFactory(
            first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}",
            organisations__organisation=TEST_USER_ORGANISATION,
            nhs_number=VALID_NHS_NUMS[-1].replace(" ", ""),
        )

        url = reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": temp_pt_same_org.id,
            },
        )

        response = client.post(
            url,
            data={"delete": "Delete"},
        )

        assert (
            response.status_code == HTTPStatus.FOUND
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` with DELETE for Case from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.FOUND} response status code, received {response.status_code}"

        # Additional test for deleting users outside of own Trust
        if test_user.first_name in [
            test_user_clinicial_audit_team_data.role_str,
            test_user_rcpch_audit_team_data.role_str,
        ]:
            # Seed a temp pt to be deleted
            temp_pt_diff_org = E12CaseFactory(
                first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}",
                organisations__organisation=DIFF_TRUST_DIFF_ORGANISATION,
                nhs_number=VALID_NHS_NUMS[-1].replace(" ", ""),
            )

            url = reverse(
                "update_case",
                kwargs={
                    "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                    "case_id": temp_pt_diff_org.id,
                },
            )

            response = client.post(
                url,
                data={"delete": "Delete"},
            )

            assert (
                response.status_code == HTTPStatus.FOUND
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}`with DELETE  for Case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.FOUND} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_patient_delete_forbidden(
    client,
):
    """Simulating different E12 users with different roles attempting to delete Patients inside own trust.

    Audit Centre Clinician & Audit Centre Lead Clinician role CANNOT delete patient in different trust.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}"

    # Seed a temp pt to be deleted
    temp_pt_same_org = E12CaseFactory(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}",
        organisations__organisation=TEST_USER_ORGANISATION,
        nhs_number=VALID_NHS_NUMS[-1].replace(" ", ""),
    )
    # Seed a temp pt to be deleted
    temp_pt_diff_org = E12CaseFactory(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}",
        organisations__organisation=DIFF_TRUST_DIFF_ORGANISATION,
        nhs_number=VALID_NHS_NUMS[-2].replace(" ", ""),
    )

    for test_user in users:
        client.force_login(test_user)

        if test_user.role in [
            test_user_audit_centre_clinician_data.role,
            test_user_audit_centre_lead_clinician_data.role,
        ]:
            url = reverse(
                "update_case",
                kwargs={
                    "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                    "case_id": temp_pt_diff_org.id,
                },
            )
        else:
            url = reverse(
                "update_case",
                kwargs={
                    "organisation_id": TEST_USER_ORGANISATION.id,
                    "case_id": temp_pt_same_org.id,
                },
            )

        response = client.post(
            url,
            data={"delete": "Delete"},
        )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` with DELETE for Case from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"
