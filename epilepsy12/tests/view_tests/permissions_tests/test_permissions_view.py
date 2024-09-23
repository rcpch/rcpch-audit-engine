"""
Tests to ensure permissions work as expected.

NOTE: if you wish to quickly seed test users inside the shell, see the `misc_py_shell_code.py` file.


## View Tests

### E12 Users 

    [x] Assert an Audit Centre Administrator can view users inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view users inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view users inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinician who is also an RCPCH Audit Team can view users inside own Trust - response.status_code == HTTPStatus.OK

    [x] Assert RCPCH Audit Team can view users inside a different Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view users inside a different Trust - response.status_code == HTTPStatus.OK 


### E12 Patient Records

    [x] Assert an Audit Centre Administrator can view patients inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an audit centre clinician can view patients inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view patients inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view patients within all Trusts - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view patients inside a different Trust - response.status_code == HTTPStatus.OK 

    [x] Assert an Audit Centre Administrator CANNOT view patients outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT view patients outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT view patients outside own Trust - response.status_code == HTTPStatus.FORBIDDEN


## Registration

    [x] Assert an Audit Centre Administrator can view 'register' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view 'register' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view 'register' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view 'register' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view 'register' outside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view 'register' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view 'register' outside own Trust - response.status_code == HTTPStatus.OK

    [x] Assert an Audit Centre Clinician cannot view 'register' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot view 'register' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot view 'register' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## First Paediatric Assessment

    [x] Assert an Audit Centre Administrator can view 'first_paediatric_assessment' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view 'first_paediatric_assessment' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view 'first_paediatric_assessment' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view 'first_paediatric_assessment' inside own Trust- response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view 'first_paediatric_assessment' outside own Trust- response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view 'first_paediatric_assessment' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view 'first_paediatric_assessment' outside own Trust - response.status_code == HTTPStatus.OK

    [x] Assert an Audit Centre Administrator cannot view 'first_paediatric_assessment' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot view 'first_paediatric_assessment' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot view 'first_paediatric_assessment' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## Epilepsy Context

    [x] Assert an Audit Centre Administrator can view 'epilepsy_context' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view 'epilepsy_context' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view 'epilepsy_context' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view 'epilepsy_context' inside own Trust- response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view 'epilepsy_context' outside own Trust- response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view 'epilepsy_context' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view 'epilepsy_context' outside own Trust - response.status_code == HTTPStatus.OK

    [x] Assert an Audit Centre Clinician cannot view 'epilepsy_context' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot view 'epilepsy_context' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot view 'epilepsy_context' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## Multiaxial Diagnosis

    [x] Assert an Audit Centre Administrator can view 'multiaxial_diagnosis' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view 'multiaxial_diagnosis' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view 'multiaxial_diagnosis' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view 'multiaxial_diagnosis' inside own Trust- response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view 'multiaxial_diagnosis' outside own Trust- response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view 'multiaxial_diagnosis' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view 'multiaxial_diagnosis' outside own Trust - response.status_code == HTTPStatus.OK


    [x] Assert an Audit Centre Clinician cannot view 'multiaxial_diagnosis' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Administrator cannot view 'multiaxial_diagnosis' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot view 'multiaxial_diagnosis' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## Episode
for each field in fields ['edit_episode','close_episode']

        [x] Assert an Audit Centre Administrator can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert an Audit Centre Clinician can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert an Audit Centre Lead Clinician can view field inside own Trust - response.status_code = 200
        [x] Assert RCPCH Audit Team can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert RCPCH Audit Team can view field inside a different Trust - response.status_code == HTTPStatus.OK
        [x] Assert Clinical Audit Team can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert Clinical Audit Team can view field outside own Trust - response.status_code == HTTPStatus.OK

        [x] Assert an Audit Centre Administrator cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
        [x] Assert an Audit Centre Clinician cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
        [x] Assert an Audit Centre Lead Clinician cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## Syndrome
for each field in fields ['edit_syndrome', 'close_syndrome']
        [x] Assert an Audit Centre Administrator can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert an Audit Centre Clinician can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert an Audit Centre Lead Clinician can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert RCPCH Audit Team can view field inside own and different Trust - response.status_code == HTTPStatus.OK
        [x] Assert Clinical Audit Team can view field inside own and different Trust - response.status_code == HTTPStatus.OK
        

        [x] Assert an Audit Centre Administrator cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
        [x] Assert an Audit Centre Clinician cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
        [x] Assert an Audit Centre Lead Clinician cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## Antiepilepsy Medicine
for each field in fields ['edit_antiepilepsy_medicine', 'close_antiepilepsy_medicine']

    [x] Assert an Audit Centre Administrator can view field inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view field inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view field inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view inside own and different Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can view inside own and different Trust - response.status_code == HTTPStatus.OK
    
    
    [x] Assert an Audit Centre Administrator cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## Comorbidity
for each field in fields ['edit_comorbidity', 'close_comorbidity', 'comorbidities']
        [x] Assert an Audit Centre Administrator can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert an Audit Centre Clinician can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert an Audit Centre Lead Clinician can view field inside own Trust - response.status_code == HTTPStatus.OK
        [x] Assert RCPCH Audit Team can view field inside own and different Trust - response.status_code == HTTPStatus.FORBIDDEN
        [x] Assert Clinical Audit Team can view field inside own and different Trust - response.status_code == HTTPStatus.OK
    
        [x] Assert an Audit Centre Administrator cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
        [x] Assert an Audit Centre Clinician cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
        [x] Assert an Audit Centre Lead Clinician cannot view field inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN


## Assessment

    [x] Assert an Audit Centre Administrator can view 'assessment' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view 'assessment' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view 'assessment' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view inside own and different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert Clinical Audit Team can view field inside own and different Trust - response.status_code == HTTPStatus.OK
    
    [x] Assert an Audit Centre Administrator cannot view 'assessment' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot view 'assessment' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot view 'assessment' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## Investigations

    [x] Assert an Audit Centre Administrator can view 'investigations' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view 'investigations' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view 'investigations' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view inside own and different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert Clinical Audit Team can view field inside own and different Trust - response.status_code == HTTPStatus.OK
    
    [x] Assert an Audit Centre Administrator cannot view 'investigations' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot view 'investigations' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot view 'investigations' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

## Management
    
    [x] Assert an Audit Centre Administrator can view 'management' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can view 'management' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can view 'management' inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can view inside own and different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert Clinical Audit Team can view field inside own and different Trust - response.status_code == HTTPStatus.OK
    
    [x] Assert an Audit Centre Administrator cannot view 'management' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Clinician cannot view 'management' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician cannot view 'management' inside a different Trust - response.status_code == HTTPStatus.FORBIDDEN

"""

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
    Case,
    Episode,
    Syndrome,
    Comorbidity,
    ComorbidityList,
    AntiEpilepsyMedicine,
    Medicine,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import twofactor_signin


@pytest.mark.parametrize(
    "URL",
    [
        ("epilepsy12_user_list"),
        ("cases"),
    ],
)
@pytest.mark.django_db
def test_users_and_case_list_views_permissions_success(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,
    URL,
):
    """
    Simulating different E12Users with different roles attempting to access the Users / Cases list of their own Trust.

    Additionally, tests RCPCH Audit Team can access lists of different Trust.


    NOTE: the `seed_groups_fixture, `seed_users_fixture`, `seed_cases_fixture` fixtures are scoped to the session, they just need to be used once to seed the db across further tests.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    # ADDENBROOKE'S
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )

    users = Epilepsy12User.objects.filter(
        organisation_employer__ods_code="RP401"
    )

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        kwargs = {"organisation_id": TEST_USER_ORGANISATION.id}

        # Request e12 User/Case list endpoint url of same Trust
        e12_user_list_response = client.get(
            reverse(
                URL,
                kwargs=kwargs,
            )
        )

        assert (
            e12_user_list_response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {URL} list of {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {e12_user_list_response.status_code}"

        # Additional test to RCPCH AUDIT TEAM / Clinical Audit Team  who should be able to view nationally
        if test_user.first_name in [
            test_user_rcpch_audit_team_data.role_str,
            test_user_clinicial_audit_team_data.role_str,
        ]:
            kwargs = {"organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id}

            # Request e12 user/case list endpoint url diff org
            e12_user_list_response = client.get(
                reverse(
                    URL,
                    kwargs=kwargs,
                )
            )

            assert (
                e12_user_list_response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {URL} list of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {e12_user_list_response.status_code}"


@pytest.mark.parametrize(
    "URL",
    [
        ("epilepsy12_user_list"),
        ("cases"),
    ],
)
@pytest.mark.django_db
def test_users_and_cases_list_view_permissions_forbidden(
    client,
    URL,
):
    """
    Simulating different E12Users with different roles attempting to access the Users / Cases list of different Trust.

    Assert these users CAN'T view the List of a different Trust.
    """

    # ADDENBROOKE'S - DIFFERENT TRUST
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )

    # RCPCH/CLINICAL AUDIT TEAM HAVE FULL ACCESS SO EXCLUDE
    users = Epilepsy12User.objects.filter(
        first_name__in=[
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
        ]
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        kwargs = {"organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id}
                
        # Request e12 user list endpoint url diff org
        e12_user_list_response_different_organisation = client.get(
            reverse(
                URL,
                kwargs=kwargs,
            )
        )

        assert (
            e12_user_list_response_different_organisation.status_code
            == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {URL} list of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {e12_user_list_response_different_organisation.status_code}"


@pytest.mark.django_db
def test_registration_view_permissions_success(client):
    """
    Assert these users CAN view registration for their own Trust.

    RCPCH Audit Team have additional test to assert can view registration outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.name}"
    )

    users = Epilepsy12User.objects.filter(
        organisation_employer__ods_code="RP401"
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Get response object
        response = client.get(
            reverse(
                "register",
                kwargs={"case_id": CASE_FROM_SAME_ORG.id},
            )
        )

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested Registration page of Case in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

        # Additional test to RCPCH AUDIT TEAM / Clinical Audit Team  who should be able to view nationally
        if test_user.first_name in [
            test_user_rcpch_audit_team_data.role_str,
            test_user_clinicial_audit_team_data.role_str,
        ]:
            DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                ods_code="RGT01",
                trust__ods_code="RGT",
            )

            # Request e12 patients list endpoint url different org
            response = client.get(
                reverse(
                    "cases",
                    kwargs={"organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id},
                )
            )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested Registration page of Case in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_registration_view_permissions_forbidden(client):
    """
    Assert these users CANT view registration for different Trust.
    """

    # GOSH
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}"
    )

    # RCPCH/CLINCAL AUDIT TEAM HAVE FULL ACCESS SO DONT INCLUDE
    users = Epilepsy12User.objects.filter(
        first_name__in=[
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
        ]
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Get response object
        response = client.get(
            reverse(
                "register",
                kwargs={"case_id": CASE_FROM_DIFF_ORG.id},
            )
        )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested registration of Case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_episode_syndrome_aem_view_permissions_success(client):
    """
    Assert these users CAN view following for Case from their own Trust:

        - episode
        - syndrome
        - aem

    RCPCH Audit Team has additional test to assert can view outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.name}"
    )

    users = Epilepsy12User.objects.filter(
        organisation_employer__ods_code="RP401"
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

    aem = AntiEpilepsyMedicine.objects.create(
        management=CASE_FROM_SAME_ORG.registration.management,
        medicine_entity=Medicine.objects.get(medicine_name="Sodium valproate"),
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        for page in ["episode", "syndrome", "antiepilepsy_medicine"]:
            # Create the object to search for
            if page == "episode":
                OBJ_SAME_ORGANISATION = episode
            elif page == "syndrome":
                OBJ_SAME_ORGANISATION = syndrome
            elif page == "antiepilepsy_medicine":
                OBJ_SAME_ORGANISATION = aem

            for action in ["edit", "close"]:
                URL = f"{action}_{page}"

                KWARGS = {f"{page}_id": OBJ_SAME_ORGANISATION.id}

                # Get response object
                response = client.get(
                    reverse(
                        URL,
                        kwargs=KWARGS,
                    )
                )

                assert (
                    response.status_code == HTTPStatus.OK
                ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {URL} page of Case from {CASE_FROM_SAME_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

                # Additional test to RCPCH AUDIT TEAM / Clinical Audit Team  who should be able to view nationally
                if test_user.first_name in [
                    test_user_rcpch_audit_team_data.role_str,
                    test_user_clinicial_audit_team_data.role_str,
                ]:
                    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                        ods_code="RGT01",
                        trust__ods_code="RGT",
                    )
                    CASE_FROM_DIFF_ORG = Case.objects.get(
                        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}"
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

                    aem = AntiEpilepsyMedicine.objects.create(
                        management=CASE_FROM_DIFF_ORG.registration.management,
                        medicine_entity=Medicine.objects.get(
                            medicine_name="Sodium valproate"
                        ),
                    )

                    # Create the object to search for
                    if page == "episode":
                        OBJ_DIFF_ORGANISATION = episode
                    elif page == "syndrome":
                        OBJ_DIFF_ORGANISATION = syndrome
                    elif page == "antiepilepsy_medicine":
                        OBJ_DIFF_ORGANISATION = aem

                    for action in ["edit", "close"]:
                        URL = f"{action}_{page}"

                        KWARGS = {f"{page}_id": OBJ_DIFF_ORGANISATION.id}

                        # Get response object
                        response = client.get(
                            reverse(
                                URL,
                                kwargs=KWARGS,
                            )
                        )

                        assert (
                            response.status_code == HTTPStatus.OK
                        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {URL} page of case from {CASE_FROM_DIFF_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.parametrize("URL", [("edit_episode"), ("close_episode")])
@pytest.mark.django_db
def test_episode_view_permissions_forbidden(client, URL):
    """
    Assert these users CANT view Episode for Case from different Trust.
    """

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}"
    )

    EPISODE_DIFF_ORG = Episode.objects.get(
        multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis
    )

    # RCPCH/CLINCAL AUDIT TEAM HAVE FULL ACCESS SO DONT INCLUDE
    users = Epilepsy12User.objects.filter(
        first_name__in=[
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
        ]
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"episode_id": EPISODE_DIFF_ORG.id},
            )
        )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested multiaxial_diagnosis page of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.parametrize("URL", [("edit_syndrome"), ("close_syndrome")])
@pytest.mark.django_db
def test_syndrome_view_permissions_forbidden(client, URL):
    """
    Assert these users CANT view syndrome for Case from different Trust.
    """

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}"
    )

    syndrome_DIFF_ORG = Syndrome.objects.get(
        multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis
    )

    # RCPCH/CLINCAL AUDIT TEAM HAVE FULL ACCESS SO DONT INCLUDE
    users = Epilepsy12User.objects.filter(
        first_name__in=[
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
        ]
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"syndrome_id": syndrome_DIFF_ORG.id},
            )
        )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested syndrome page of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.parametrize(
    "URL", [("edit_antiepilepsy_medicine"), ("close_antiepilepsy_medicine")]
)
@pytest.mark.django_db
def test_antiepilepsy_medicine_view_permissions_forbidden(client, URL):
    """
    Assert these users CANT view antiepilepsy_medicine for Case from different Trust.
    """

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}"
    )

    antiepilepsy_medicine_DIFF_ORG = AntiEpilepsyMedicine.objects.create(
        management=CASE_FROM_DIFF_ORG.registration.management,
        medicine_entity=Medicine.objects.get(medicine_name="Sodium valproate"),
    )

    # RCPCH/CLINCAL AUDIT TEAM HAVE FULL ACCESS SO DONT INCLUDE
    users = Epilepsy12User.objects.filter(
        first_name__in=[
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
        ]
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"antiepilepsy_medicine_id": antiepilepsy_medicine_DIFF_ORG.id},
            )
        )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested antiepilepsy_medicine page ({URL}) of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.parametrize(
    "URL",
    [
        ("edit_comorbidity"),
        ("close_comorbidity"),
        ("comorbidities"),
    ],
)
@pytest.mark.django_db
def test_comborbidity_view_permissions_success(client, URL):
    """
    Assert these users CAN view comorbidities for Case from their own Trust.

    RCPCH Audit Team have additional test to assert can view comborbiditys outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.name}"
    )

    COMORBIDITY_SAME_ORG = Comorbidity.objects.create(
        multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis,
        comorbidityentity=ComorbidityList.objects.filter(
            conceptId="1148757008"
        ).first(),
    )

    users = Epilepsy12User.objects.filter(
        organisation_employer__ods_code="RP401"
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Get response object
        if URL == "comorbidities":
            response = client.get(
                reverse(
                    URL,
                    kwargs={
                        "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id
                    },
                )
            )
        else:
            response = client.get(
                reverse(
                    URL,
                    kwargs={"comorbidity_id": COMORBIDITY_SAME_ORG.id},
                )
            )

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested comborbidity page of user from {CASE_FROM_SAME_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

        # Additional test to RCPCH AUDIT TEAM / Clinical Audit Team  who should be able to view nationally
        if test_user.first_name in [
            test_user_rcpch_audit_team_data.role_str,
            test_user_clinicial_audit_team_data.role_str,
        ]:
            DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                ods_code="RGT01",
                trust__ods_code="RGT",
            )
            CASE_FROM_DIFF_ORG = Case.objects.get(
                first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}"
            )

            comborbidity_DIFF_ORG = Comorbidity.objects.create(
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
                comorbidityentity=ComorbidityList.objects.filter(
                    conceptId="1148757008"
                ).first(),
            )

            # Request e12 patients list endpoint url different org
            if URL == "comorbidities":
                response = client.get(
                    reverse(
                        URL,
                        kwargs={
                            "multiaxial_diagnosis_id": CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis.id
                        },
                    )
                )
            else:
                response = client.get(
                    reverse(
                        URL,
                        kwargs={"comorbidity_id": comborbidity_DIFF_ORG.id},
                    )
                )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested comborbidity page of {CASE_FROM_DIFF_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.parametrize(
    "URL", [("edit_comorbidity"), ("close_comorbidity"), ("comorbidities")]
)
@pytest.mark.django_db
def test_comborbidity_view_permissions_forbidden(client, URL):
    """
    Assert these users CANT view comborbidity for Case from different Trust.
    """

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}"
    )

    COMORBIDITY_DIFF_ORG = Comorbidity.objects.create(
        multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
        comorbidityentity=ComorbidityList.objects.filter(
            conceptId="1148757008"
        ).first(),
    )

    # RCPCH/CLINCAL AUDIT TEAM HAVE FULL ACCESS SO DONT INCLUDE
    users = Epilepsy12User.objects.filter(
        first_name__in=[
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
        ]
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        # Get response object
        if URL == "comorbidities":
            response = client.get(
                reverse(
                    URL,
                    kwargs={
                        "multiaxial_diagnosis_id": CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis.id
                    },
                )
            )
        else:
            response = client.get(
                reverse(
                    URL,
                    kwargs={"comorbidity_id": COMORBIDITY_DIFF_ORG.id},
                )
            )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested comorbidity page of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_multiple_views_permissions_success(client):
    """
    Assert these users CAN view the following pages for their own Trust:

        - first_paediatric_assessment
        - assessment
        - management
        - investigations
        - epilepsy_context
        - multiaxial_diagnosis

    RCPCH Audit Team has additional test to assert can view assessment outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.name}"
    )

    users = Epilepsy12User.objects.filter(
        organisation_employer__ods_code="RP401"
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        for url_name in [
            "assessment",
            "investigations",
            "management",
            "first_paediatric_assessment",
            "epilepsy_context",
            "multiaxial_diagnosis",
        ]:
            # Get response object
            response = client.get(
                reverse(
                    url_name,
                    kwargs={"case_id": CASE_FROM_SAME_ORG.id},
                )
            )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {url_name} page of user from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

            # Additional test to RCPCH AUDIT TEAM / Clinical Audit Team  who should be able to view nationally
            if test_user.first_name in [
                test_user_rcpch_audit_team_data.role_str,
                test_user_clinicial_audit_team_data.role_str,
            ]:
                DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                    ods_code="RGT01",
                    trust__ods_code="RGT",
                )
                CASE_FROM_DIFF_ORG = Case.objects.get(
                    first_name=f"child_{TEST_USER_ORGANISATION.name}"
                )

                # Request e12 patients list endpoint url different org
                response = client.get(
                    reverse(
                        url_name,
                        kwargs={"case_id": CASE_FROM_DIFF_ORG.id},
                    )
                )

                assert (
                    response.status_code == HTTPStatus.OK
                ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {url_name} page of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_multiple_views_permissions_forbidden(client):
    """
    Assert these users CANT view these pages for different Trust.

        - first_paediatric_assessment
        - assessment
        - management
        - investigations
        - epilepsy_context
        - multiaxial_diagnosis
    """

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ods_code="RGT01",
        trust__ods_code="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.name}"
    )

    # RCPCH/CLINCAL AUDIT TEAM HAVE FULL ACCESS SO DONT INCLUDE
    users = Epilepsy12User.objects.filter(
        first_name__in=[
            test_user_audit_centre_administrator_data.role_str,
            test_user_audit_centre_clinician_data.role_str,
            test_user_audit_centre_lead_clinician_data.role_str,
        ]
    )

    for test_user in users:
        client.force_login(test_user)

        # 2fa enable
        twofactor_signin(client, test_user)

        for url_name in [
            "assessment",
            "investigations",
            "management",
            "first_paediatric_assessment",
            "epilepsy_context",
            "multiaxial_diagnosis",
        ]:
            # Get response object
            response = client.get(
                reverse(
                    url_name,
                    kwargs={"case_id": CASE_FROM_DIFF_ORG.id},
                )
            )

            assert (
                response.status_code == HTTPStatus.FORBIDDEN
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {url_name} page of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"
