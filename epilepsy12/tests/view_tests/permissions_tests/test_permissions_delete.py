"""
## Delete Tests

    [x] Assert an Audit Centre Lead Clinician can deactivate users inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can deactivate users inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can deactivate users outside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can deactivate users inside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can deactivate users outside own Trust - HTTPStatus.OK

    [x] Assert an Audit Centre Administrator CANNOT deactivate users - HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT deactivate users - HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT deactivate users outside own Trust - HTTPStatus.FORBIDDEN
    
    

    [x] Assert an Audit Centre Lead Clinician can deactivate patients inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can deactivate patients inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can deactivate patients outside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can deactivate patients inside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can deactivate patients outside own Trust - HTTPStatus.OK
    
    [x] Assert an Audit Centre Administrator CANNOT deactivate patients - HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT deactivate patients outside own Trust - HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT deactivate patients outside own Trust - HTTPStatus.FORBIDDEN


# Episode

    [x] Assert an Audit Centre Lead Clinician can 'remove_episode' inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can 'remove_episode' inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can 'remove_episode' outside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can 'remove_episode' inside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can 'remove_episode' outside own Trust - HTTPStatus.OK
    
    [x] Assert an Audit Centre Administrator CANNOT  'remove_episode' - HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT  'remove_episode' outside own Trust - HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT  'remove_episode' outside own Trust - HTTPStatus.FORBIDDEN

# Syndrome

    [x] Assert an Audit Centre Lead Clinician can 'remove_syndrome' inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can 'remove_syndrome' inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can 'remove_syndrome' outside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can 'remove_syndrome' inside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can 'remove_syndrome' outside own Trust - HTTPStatus.OK
    
    [x] Assert an Audit Centre Administrator CANNOT  'remove_syndrome' - HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT  'remove_syndrome' outside own Trust - HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT  'remove_syndrome' outside own Trust - HTTPStatus.FORBIDDEN

# Comorbidity

    [x] Assert an Audit Centre Lead Clinician can 'remove_comorbidity' inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can 'remove_comorbidity' inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can 'remove_comorbidity' outside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can 'remove_comorbidity' inside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can 'remove_comorbidity' outside own Trust - HTTPStatus.OK
    
    [x] Assert an Audit Centre Administrator CANNOT  'remove_comorbidity' - HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT  'remove_comorbidity' outside own Trust - HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT  'remove_comorbidity' outside own Trust - HTTPStatus.FORBIDDEN
    

# Antiepilepsy Medicine

    [x] Assert an Audit Centre Lead Clinician can 'remove_antiepilepsy_medicine' inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can 'remove_antiepilepsy_medicine' inside own Trust - HTTPStatus.OK
    [x] Assert RCPCH Audit Team can 'remove_antiepilepsy_medicine' outside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can 'remove_antiepilepsy_medicine' inside own Trust - HTTPStatus.OK
    [x] Assert Clinical Audit Team can 'remove_antiepilepsy_medicine' outside own Trust - HTTPStatus.OK
    
    [x] Assert an Audit Centre Administrator CANNOT  'remove_antiepilepsy_medicine' - HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT  'remove_antiepilepsy_medicine' outside own Trust - HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT  'remove_antiepilepsy_medicine' outside own Trust - HTTPStatus.FORBIDDEN
"""

# python imports
import pytest
from http import HTTPStatus
from datetime import date

# django imports
from django.urls import reverse

# E12 Imports
from epilepsy12.tests.factories import (
    E12UserFactory,
    E12CaseFactory,
)
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
    Episode,
    Syndrome,
    Comorbidity,
    AntiEpilepsyMedicine,
    Medicine,
    ComorbidityList,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


@pytest.mark.django_db
def test_user_deactivate_success(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,
):
    """Simulating different E12 users with different roles attempting to deactivate inside own trust.

    Additionally, RCPCH Audit Team and Clinical Audit Team roles should be able to deactivate user in different trust.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

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


@pytest.mark.django_db
def test_user_deactivate_forbidden(
    client,
):
    """Simulating different E12 users with different roles attempting to deactivate Users inside own trust.

    Audit Centre Lead Clinician role CANNOT delete user in different trust.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # Seed a temp User for attempt to deactivate
    temp_user_same_org = E12UserFactory(
        first_name="temp_user",
        email=f"temp_user_same_org@temp.com",
        role=test_user_audit_centre_administrator_data.role,
        is_active=1,
        organisation_employer=TEST_USER_ORGANISATION,
        groups=[test_user_audit_centre_administrator_data.group_name],
    )
    # Seed a temp User to be deactivated
    temp_user_same_org = E12UserFactory(
        first_name="temp_user",
        email=f"temp_user_diff_org@temp.com",
        role=test_user_audit_centre_administrator_data.role,
        is_active=1,
        organisation_employer=DIFF_TRUST_DIFF_ORGANISATION,
        groups=[test_user_audit_centre_administrator_data.group_name],
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

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
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Seed a temp pt to be deleted
        temp_pt_same_org = E12CaseFactory(
            first_name=f"child_{TEST_USER_ORGANISATION.name}",
            organisations__organisation=TEST_USER_ORGANISATION,
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
            headers={"Hx-Trigger-Name": "delete", "Hx-Request": "true"},
        )

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` with DELETE for Case from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.OK} response status code, received {response.status_code}"

        # Additional test for deleting users outside of own Trust
        if test_user.first_name in [
            test_user_clinicial_audit_team_data.role_str,
            test_user_rcpch_audit_team_data.role_str,
        ]:
            # Seed a temp pt to be deleted
            temp_pt_diff_org = E12CaseFactory(
                first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}",
                organisations__organisation=DIFF_TRUST_DIFF_ORGANISATION,
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
                headers={"Hx-Trigger-Name": "delete", "Hx-Request": "true"},
            )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}`with DELETE  for Case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.OK} response status code, received {response.status_code}"


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
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_administrator_data.role_str,
        test_user_audit_centre_clinician_data.role_str,
        test_user_audit_centre_lead_clinician_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    # Seed a temp pt to be deleted
    temp_pt_same_org = E12CaseFactory(
        first_name=f"child_{TEST_USER_ORGANISATION.name}",
        organisations__organisation=TEST_USER_ORGANISATION,
    )
    # Seed a temp pt to be deleted
    temp_pt_diff_org = E12CaseFactory(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}",
        organisations__organisation=DIFF_TRUST_DIFF_ORGANISATION,
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        if test_user.first_name in [
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
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
            headers={"Hx-Trigger-Name": "delete", "Hx-Request": "true"},
        )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` with DELETE for Case from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"


@pytest.mark.django_db
def test_episode_delete_success(
    client,
):
    """Simulating different E12 users with different roles attempting to delete Episode inside own trust.

    Additionally, RCPCH Audit Team and Clinical Audit Team roles should be able to delete Episode in different trust.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )

    user_first_names_for_test = [
        test_user_audit_centre_lead_clinician_data.role_str,
        test_user_rcpch_audit_team_data.role_str,
        test_user_clinicial_audit_team_data.role_str,
    ]
    users = Epilepsy12User.objects.filter(first_name__in=user_first_names_for_test)

    assert len(users) == len(
        user_first_names_for_test
    ), f"Incorrect queryset of test users. Requested {len(user_first_names_for_test)} users, queryset includes {len(users)}: {users}"

    URLS = [
        "episode",
        "comorbidity",
        "syndrome",
        "antiepilepsy_medicine",
    ]

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Create a Case with Episode
        CASE_FROM_SAME_ORG = E12CaseFactory(
            first_name=f"temp_{TEST_USER_ORGANISATION}",
            organisations__organisation=TEST_USER_ORGANISATION,
        )
        # Create objs to search for
        episode = Episode.objects.create(
            episode_definition="a",
            multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis,
        )

        syndrome = Syndrome.objects.create(
            syndrome_diagnosis_date=date(
                2023, 2, 1
            ),  # arbitrary answer just to ensure at least 1 completed field so not removed inside close_syndrome view
            multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis,
        )

        comorbidity = Comorbidity.objects.create(
            multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis,
            comorbidityentity=ComorbidityList.objects.filter(
                conceptId="1148757008"
            ).first(),
        )

        aem = AntiEpilepsyMedicine.objects.create(
            management=CASE_FROM_SAME_ORG.registration.management,
            medicine_entity=Medicine.objects.get(medicine_name="Sodium valproate"),
        )

        for url in URLS:
            if url == "episode":
                OBJ_TO_DEL = episode
            elif url == "comorbidity":
                OBJ_TO_DEL = syndrome
            elif url == "syndrome":
                OBJ_TO_DEL = comorbidity
            else:
                OBJ_TO_DEL = aem

        url = reverse(
            f"remove_{url}",
            kwargs={f"{url}_id": OBJ_TO_DEL.id},
        )

        response = client.post(
            url,
        )

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` with DELETE for Case from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.OK} response status code, received {response.status_code}"

        # Reset Case for next User
        CASE_FROM_SAME_ORG.delete()

        # Additional test for deleting Episode outside of own Trust
        if test_user.first_name in [
            test_user_clinicial_audit_team_data.role_str,
            test_user_rcpch_audit_team_data.role_str,
        ]:
            # Create a Case with Episode
            CASE_FROM_DIFF_ORG = E12CaseFactory(
                first_name=f"temp_{DIFF_TRUST_DIFF_ORGANISATION}",
                organisations__organisation=DIFF_TRUST_DIFF_ORGANISATION,
            )
            # Create objs to search for
            episode = Episode.objects.create(
                episode_definition="a",
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
            )

            syndrome = Syndrome.objects.create(
                syndrome_diagnosis_date=date(
                    2023, 2, 1
                ),  # arbitrary answer just to ensure at least 1 completed field so not removed inside close_syndrome view
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
            )

            comorbidity = Comorbidity.objects.create(
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
                comorbidityentity=ComorbidityList.objects.filter(
                    conceptId="1148757008"
                ).first(),
            )

            aem = AntiEpilepsyMedicine.objects.create(
                management=CASE_FROM_DIFF_ORG.registration.management,
                medicine_entity=Medicine.objects.get(medicine_name="Sodium valproate"),
            )

            for url in URLS:
                if url == "episode":
                    OBJ_TO_DEL = episode
                elif url == "comorbidity":
                    OBJ_TO_DEL = syndrome
                elif url == "syndrome":
                    OBJ_TO_DEL = comorbidity
                else:
                    OBJ_TO_DEL = aem

            url = reverse(
                f"remove_{url}",
                kwargs={f"{url}_id": OBJ_TO_DEL.id},
            )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}`with DELETE  for Case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.OK} response status code, received {response.status_code}"

            # Reset Case and Episode
            CASE_FROM_DIFF_ORG.delete()
