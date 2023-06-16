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

[x] Assert an Audit Centre Administrator can view users inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Clinician can view users inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Lead Clinician can view users inside own Trust - response.status_code == 200
    [x] Assert an RCPCH Audit Lead can view users inside own Trust - response.status_code == 200
    [x] Assert an RCPCH Audit Lead can view users inside a different Trust - response.status_code == 200

[x] Assert an Audit Centre Administrator can view patients inside own Trust - response.status_code == 200
[x] Assert an audit centre clinician can view patients inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician can view patients inside own Trust - response.status_code == 200
[x] Assert an RCPCH Audit Lead can view patients within all Trusts - response.status_code == 200


[x] Assert an Audit Centre Administrator CANNOT view patients outside own Trust - response.status_code == 403
[x] Assert an audit centre clinician CANNOT view patients outside own Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician CANNOT view patients outside own Trust - response.status_code == 403

# E12 Patient Records

## Registration

[x] Assert an Audit Centre Administrator can view 'register' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Clinician can view 'register' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician can view 'register' inside own Trust - response.status_code == 200
[x] Assert an RCPCH Audit Lead can view 'register' inside own Trust - response.status_code == 200
[x] Assert an RCPCH Audit Lead can view 'register' outside own Trust - response.status_code == 200

[x] Assert an Audit Centre Clinician cannot view 'register' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Administrator cannot view 'register' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician cannot view 'register' inside a different Trust - response.status_code == 403

## First Paediatric Assessment

[x] Assert an Audit Centre Administrator can view 'first_paediatric_assessment' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Clinician can view 'first_paediatric_assessment' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician can view 'first_paediatric_assessment' inside own Trust - response.status_code == 200
[x] Assert an RCPCH Audit Lead can view 'first_paediatric_assessment' inside own Trust- response.status_code == 200
[x] Assert an RCPCH Audit Lead can view 'first_paediatric_assessment' outside own Trust- response.status_code == 200

[x] Assert an Audit Centre Administrator cannot view 'first_paediatric_assessment' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Clinician cannot view 'first_paediatric_assessment' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician cannot view 'first_paediatric_assessment' inside a different Trust - response.status_code == 403

## Epilepsy Context

[x] Assert an Audit Centre Administrator can view 'epilepsy_context' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Clinician can view 'epilepsy_context' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician can view 'epilepsy_context' inside own Trust - response.status_code == 200
[x] Assert an RCPCH Audit Lead can view 'epilepsy_context' inside own Trust- response.status_code == 200
[x] Assert an RCPCH Audit Lead can view 'epilepsy_context' outside own Trust- response.status_code == 200

[x] Assert an Audit Centre Clinician cannot view 'epilepsy_context' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Administrator cannot view 'epilepsy_context' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician cannot view 'epilepsy_context' inside a different Trust - response.status_code == 403

## Multiaxial Diagnosis

[x] Assert an Audit Centre Administrator can view 'multiaxial_diagnosis' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Clinician can view 'multiaxial_diagnosis' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician can view 'multiaxial_diagnosis' inside own Trust - response.status_code == 200
[x] Assert an RCPCH Audit Lead can view 'multiaxial_diagnosis' inside own Trust- response.status_code == 200
[x] Assert an RCPCH Audit Lead can view 'multiaxial_diagnosis' outside own Trust- response.status_code == 200


[x] Assert an Audit Centre Clinician cannot view 'multiaxial_diagnosis' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Administrator cannot view 'multiaxial_diagnosis' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician cannot view 'multiaxial_diagnosis' inside a different Trust - response.status_code == 403

## Episode
for each field in fields ['edit_episode','close_episode']

    [x] Assert an Audit Centre Administrator can view field inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Clinician can view field inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Lead Clinician can view field inside own Trust - response.status_code = 200
    [x] Assert an Audit Centre Administrator can view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Lead Clinician can view field inside a different Trust - response.status_code == 403

    [x] Assert an Audit Centre Administrator cannot view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Clinician cannot view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Lead Clinician cannot view field inside a different Trust - response.status_code == 403

## Syndrome
for each field in fields ['edit_syndrome', 'close_syndrome']
    [x] Assert an Audit Centre Administrator can view field inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Clinician can view field inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Lead Clinician can view field inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Administrator can view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Lead Clinician can view field inside a different Trust - response.status_code == 403

    [x] Assert an Audit Centre Administrator cannot view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Clinician cannot view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Lead Clinician cannot view field inside a different Trust - response.status_code == 403

## Comorbidity
for each field in fields ['edit_comorbidity', 'close_comorbidity', 'comorbidities']
    [x] Assert an Audit Centre Administrator can view field inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Clinician can view field inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Lead Clinician can view field inside own Trust - response.status_code == 200
    [x] Assert an Audit Centre Administrator can view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Lead Clinician can view field inside a different Trust - response.status_code == 403
    
    [x] Assert an Audit Centre Administrator cannot view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Clinician cannot view field inside a different Trust - response.status_code == 403
    [x] Assert an Audit Centre Lead Clinician cannot view field inside a different Trust - response.status_code == 403


## Assessment
[x] Assert an Audit Centre Administrator can view 'assessment' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Administrator cannot view 'assessment' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Clinician can view 'assessment' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Clinician cannot view 'assessment' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician can view 'assessment' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician cannot view 'assessment' inside a different Trust - response.status_code == 403
[x] Assert an RCPCH Audit Lead can view 'assessment' - response.status_code == 200

## Investigations
[x] Assert an Audit Centre Administrator can view 'investigations' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Administrator cannot view 'investigations' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Clinician can view 'investigations' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Clinician cannot view 'investigations' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician can view 'investigations' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician cannot view 'investigations' inside a different Trust - response.status_code == 403
[x] Assert an RCPCH Audit Lead can view 'investigations' - response.status_code == 200

## Management
[x] Assert an Audit Centre Administrator can view 'management' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Administrator cannot view 'management' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Clinician can view 'management' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Clinician cannot view 'management' inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician can view 'management' inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician cannot view 'management' inside a different Trust - response.status_code == 403
[x] Assert an RCPCH Audit Lead can view 'management' - response.status_code == 200

## Antiepilepsy Medicine
for each field in fields ['edit_antiepilepsy_medicine', 'close_antiepilepsy_medicine']
[x] Assert an Audit Centre Administrator can view field inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Administrator cannot view field inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Clinician can view field inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Clinician cannot view field inside a different Trust - response.status_code == 403
[x] Assert an Audit Centre Lead Clinician can view field inside own Trust - response.status_code == 200
[x] Assert an Audit Centre Lead Clinician cannot view field inside a different Trust - response.status_code == 403
[x] Assert an RCPCH Audit Lead can view field - response.status_code == 200

"""

# python imports
import pytest

# django imports
from django.urls import reverse

# E12 imports
# E12 Imports
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_rcpch_audit_lead_data,
)
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    Case,
    Episode,
    Syndrome,
    Comorbidity,
    ComorbidityEntity,
    AntiEpilepsyMedicine,
    MedicineEntity,
)


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
    # Simulating different E12Users with different roles attempting to access the Users / Cases list of their own Trust. 
    # 
    # Additionally, tests RCPCH Audit Leads can access lists of different Trust.


    NOTE: the `seed_groups_fixture, `seed_users_fixture`, `seed_cases_fixture` fixtures are scoped to the session, they just need to be used once to seed the db across further tests.
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

    users = Epilepsy12User.objects.all()

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        # Request e12 User/Case list endpoint url of same Trust
        e12_user_list_response = client.get(
            reverse(
                URL,
                kwargs={"organisation_id": TEST_USER_ORGANISATION.id},
            )
        )

        assert (
            e12_user_list_response.status_code == 200
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {URL} list of {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {e12_user_list_response.status_code}"

        # Additional test to RCPCH AUDIT LEADs who should be able to view nationally
        if test_user.role == test_user_rcpch_audit_lead_data.role:
            # Request e12 user/case list endpoint url diff org
            e12_user_list_response = client.get(
                reverse(
                    URL,
                    kwargs={"organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id},
                )
            )

            assert (
                e12_user_list_response.status_code == 200
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {URL} list of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {e12_user_list_response.status_code}"

@pytest.mark.parametrize(
    "URL",
    [
        ("epilepsy12_user_list"),
        ("cases"),
    ],
)
@pytest.mark.django_db
def test_users_and_cases_list_view_permissions_forbidden(client,URL,):
    """
    Simulating different E12Users with different roles attempting to access the Users / Cases list of different Trust. 

    Assert these users CAN'T view the List of a different Trust.
    """

    # ADDENBROOKE'S - DIFFERENT TRUST
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    # RCPCH AUDIT LEADS HAVE FULL ACCESS SO EXCLUDE
    users = Epilepsy12User.objects.all().exclude(first_name="RCPCH_AUDIT_LEAD")

    for test_user in users:
        client.force_login(test_user)

        # Request e12 user list endpoint url diff org
        e12_user_list_response_different_organisation = client.get(
            reverse(
                URL,
                kwargs={"organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id},
            )
        )

        assert (
            e12_user_list_response_different_organisation.status_code == 403
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {URL} list of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {e12_user_list_response_different_organisation.status_code}"


@pytest.mark.django_db
def test_registration_view_permissions_success(client):
    """
    Assert these users CAN view registration for their own Trust.

    RCPCH Audit Lead has additional test to assert can view registration outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    users = Epilepsy12User.objects.all()

    for test_user in users:
        client.force_login(test_user)

        # Get response object
        response = client.get(
            reverse(
                "register",
                kwargs={"case_id": CASE_FROM_SAME_ORG.id},
            )
        )

        assert (
            response.status_code == 200
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested Registration page of Case in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

        # Additional test: assert different organisation if RCPCH AUDIT LEAD
        # ADDENBROOKE'S
        if test_user.role == test_user_rcpch_audit_lead_data.role:
            DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                ODSCode="RGT01",
                ParentOrganisation_ODSCode="RGT",
            )

            # Request e12 patients list endpoint url different org
            response = client.get(
                reverse(
                    "cases",
                    kwargs={"organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id},
                )
            )

            assert (
                response.status_code == 200
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested Registration page of Case in {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_registration_view_permissions_forbidden(client):
    """
    Assert these users CANT view registration for different Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    # RCPCH AUDIT LEADS HAVE FULL ACCESS SO EXCLUDE
    users = Epilepsy12User.objects.all().exclude(first_name="RCPCH_AUDIT_LEAD")

    for test_user in users:
        client.force_login(test_user)

        # Get response object
        response = client.get(
            reverse(
                "register",
                kwargs={"case_id": CASE_FROM_DIFF_ORG.id},
            )
        )

        assert (
            response.status_code == 403
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested registration of Case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.parametrize("URL", [("edit_episode"), ("close_episode")])
@pytest.mark.django_db
def test_episode_view_permissions_success(client, URL):
    """
    Assert these users CAN view episode for Case from their own Trust.

    RCPCH Audit Lead has additional test to assert can view episodes outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    users = Epilepsy12User.objects.all()

    for test_user in users:
        EPISODE_SAME_ORG = Episode.objects.create(
            multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis
        )

        client.force_login(test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"episode_id": EPISODE_SAME_ORG.id},
            )
        )

        assert (
            response.status_code == 200
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested episode page of user from {CASE_FROM_SAME_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

        # Additional test: assert different organisation if RCPCH AUDIT LEAD
        # ADDENBROOKE'S
        if test_user.role == test_user_rcpch_audit_lead_data.role:
            DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                ODSCode="RGT01",
                ParentOrganisation_ODSCode="RGT",
            )
            CASE_FROM_DIFF_ORG = Case.objects.get(
                first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
            )

            EPISODE_DIFF_ORG = Episode.objects.get(
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis
            )

            # Request e12 patients list endpoint url different org
            response = client.get(
                reverse(
                    URL,
                    kwargs={"episode_id": EPISODE_DIFF_ORG.id},
                )
            )

            assert (
                response.status_code == 200
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested episode page of {CASE_FROM_DIFF_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.parametrize("URL", [("edit_episode"), ("close_episode")])
@pytest.mark.django_db
def test_episode_view_permissions_forbidden(client, URL):
    """
    Assert these users CANT view Episode for Case from different Trust.
    """

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )
    EPISODE_DIFF_ORG = Episode.objects.get(
        multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis
    )

    # RCPCH AUDIT LEADS HAVE FULL ACCESS SO EXCLUDE
    users = Epilepsy12User.objects.all().exclude(first_name="RCPCH_AUDIT_LEAD")

    for test_user in users:
        client.force_login(test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"episode_id": EPISODE_DIFF_ORG.id},
            )
        )

        assert (
            response.status_code == 403
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested multiaxial_diagnosis page of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.parametrize("URL", [("edit_syndrome"), ("close_syndrome")])
@pytest.mark.django_db
def test_syndrome_view_permissions_success(client, URL):
    """
    Assert these users CAN view syndrome for Case from their own Trust.

    RCPCH Audit Lead has additional test to assert can view syndromes outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    users = Epilepsy12User.objects.all()

    for test_user in users:
        SYNDROME_SAME_ORG = Syndrome.objects.create(
            multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis
        )

        client.force_login(test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"syndrome_id": SYNDROME_SAME_ORG.id},
            )
        )

        assert (
            response.status_code == 200
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested syndrome page of user from {CASE_FROM_SAME_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

        # Additional test: assert different organisation if RCPCH AUDIT LEAD
        # ADDENBROOKE'S
        if test_user.role == test_user_rcpch_audit_lead_data.role:
            DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                ODSCode="RGT01",
                ParentOrganisation_ODSCode="RGT",
            )
            CASE_FROM_DIFF_ORG = Case.objects.get(
                first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
            )

            SYNDROME_DIFF_ORG = Syndrome.objects.get(
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis
            )

            # Request e12 patients list endpoint url different org
            response = client.get(
                reverse(
                    URL,
                    kwargs={"syndrome_id": SYNDROME_DIFF_ORG.id},
                )
            )

            assert (
                response.status_code == 200
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested syndrome page of {CASE_FROM_DIFF_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.parametrize("URL", [("edit_syndrome"), ("close_syndrome")])
@pytest.mark.django_db
def test_syndrome_view_permissions_forbidden(client, URL):
    """
    Assert these users CANT view syndrome for Case from different Trust.
    """

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )
    syndrome_DIFF_ORG = Syndrome.objects.get(
        multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis
    )

    # RCPCH AUDIT LEADS HAVE FULL ACCESS SO EXCLUDE
    users = Epilepsy12User.objects.all().exclude(first_name="RCPCH_AUDIT_LEAD")

    for test_user in users:
        client.force_login(test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"syndrome_id": syndrome_DIFF_ORG.id},
            )
        )

        assert (
            response.status_code == 403
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested syndrome page of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.parametrize(
    "URL", [("edit_comorbidity"), ("close_comorbidity"), ("comorbidities")]
)
@pytest.mark.django_db
def test_comborbidity_view_permissions_success(client, URL):
    """
    Assert these users CAN view comorbidities for Case from their own Trust.

    RCPCH Audit Lead has additional test to assert can view comborbiditys outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )
    COMORBIDITY_SAME_ORG = Comorbidity.objects.create(
        multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis,
        comorbidityentity=ComorbidityEntity.objects.filter(
            conceptId="1148757008"
        ).first(),
    )

    users = Epilepsy12User.objects.all()

    for test_user in users:
        client.force_login(test_user)

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
            response.status_code == 200
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested comborbidity page of user from {CASE_FROM_SAME_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

        # Additional test: assert different organisation if RCPCH AUDIT LEAD
        # ADDENBROOKE'S
        if test_user.role == test_user_rcpch_audit_lead_data.role:
            DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                ODSCode="RGT01",
                ParentOrganisation_ODSCode="RGT",
            )
            CASE_FROM_DIFF_ORG = Case.objects.get(
                first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
            )

            comborbidity_DIFF_ORG = Comorbidity.objects.create(
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
                comorbidityentity=ComorbidityEntity.objects.filter(
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
                response.status_code == 200
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
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )
    COMORBIDITY_DIFF_ORG = Comorbidity.objects.create(
        multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis,
        comorbidityentity=ComorbidityEntity.objects.filter(
            conceptId="1148757008"
        ).first(),
    )

    # RCPCH AUDIT LEADS HAVE FULL ACCESS SO EXCLUDE
    users = Epilepsy12User.objects.all().exclude(first_name="RCPCH_AUDIT_LEAD")

    for test_user in users:
        client.force_login(test_user)

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
            response.status_code == 403
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested comorbidity page of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_assessment_investigations_management_view_permissions_success(client):
    """
    Assert these users CAN view the following pages for their own Trust:

        - first_paediatric_assessment
        - assessment
        - management
        - investigations
        - epilepsy_context
        - multiaxial_diagnosis

    RCPCH Audit Lead has additional test to assert can view assessment outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    users = Epilepsy12User.objects.all()

    for test_user in users:
        client.force_login(test_user)

        for url_name in ["assessment", "investigations", "management", "first_paediatric_assessment", "epilepsy_context", "multiaxial_diagnosis"]:
            # Get response object
            response = client.get(
                reverse(
                    url_name,
                    kwargs={"case_id": CASE_FROM_SAME_ORG.id},
                )
            )
            
            print(url_name, response.status_code)

            assert (
                response.status_code == 200
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {url_name} page of user from {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

            # Additional test: assert different organisation if RCPCH AUDIT LEAD
            # ADDENBROOKE'S
            if test_user.role == test_user_rcpch_audit_lead_data.role:
                DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                    ODSCode="RGT01",
                    ParentOrganisation_ODSCode="RGT",
                )
                CASE_FROM_DIFF_ORG = Case.objects.get(
                    first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
                )

                # Request e12 patients list endpoint url different org
                response = client.get(
                    reverse(
                        url_name,
                        kwargs={"case_id": CASE_FROM_DIFF_ORG.id},
                    )
                )

                assert (
                    response.status_code == 200
                ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {url_name} page of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.django_db
def test_assessment_investigations_management_view_permissions_forbidden(client):
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
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    # RCPCH AUDIT LEADS HAVE FULL ACCESS SO EXCLUDE
    users = Epilepsy12User.objects.all().exclude(first_name="RCPCH_AUDIT_LEAD")

    for test_user in users:
        client.force_login(test_user)

        for url_name in ["assessment", "investigations", "management", "first_paediatric_assessment", "epilepsy_context", "multiaxial_diagnosis"]:
            # Get response object
            response = client.get(
                reverse(
                    url_name,
                    kwargs={"case_id": CASE_FROM_DIFF_ORG.id},
                )
            )

            assert (
                response.status_code == 403
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested {url_name} page of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"


@pytest.mark.parametrize(
    "URL", [("edit_antiepilepsy_medicine"), ("close_antiepilepsy_medicine")]
)
@pytest.mark.django_db
def test_antiepilepsy_medicine_view_permissions_success(client, URL):
    """
    Assert these users CAN view antiepilepsy_medicine for Case from their own Trust.

    RCPCH Audit Lead has additional test to assert can view antiepilepsy_medicines outside own Trust.
    """

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    users = Epilepsy12User.objects.all()

    for test_user in users:
        antiepilepsy_medicine_SAME_ORG = AntiEpilepsyMedicine.objects.create(
            management=CASE_FROM_SAME_ORG.registration.management,
            medicine_entity=MedicineEntity.objects.get(
                medicine_name="Sodium valproate"
            ),
        )

        client.force_login(test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"antiepilepsy_medicine_id": antiepilepsy_medicine_SAME_ORG.id},
            )
        )

        assert (
            response.status_code == 200
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested antiepilepsy_medicine page url ({URL}) of user from {CASE_FROM_SAME_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"

        # Additional test: assert different organisation if RCPCH AUDIT LEAD
        # ADDENBROOKE'S
        if test_user.role == test_user_rcpch_audit_lead_data.role:
            DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
                ODSCode="RGT01",
                ParentOrganisation_ODSCode="RGT",
            )
            CASE_FROM_DIFF_ORG = Case.objects.get(
                first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
            )

            antiepilepsy_medicine_DIFF_ORG = AntiEpilepsyMedicine.objects.create(
                management=CASE_FROM_DIFF_ORG.registration.management,
                medicine_entity=MedicineEntity.objects.get(
                    medicine_name="Sodium valproate"
                ),
            )

            # Request e12 patients list endpoint url different org
            response = client.get(
                reverse(
                    URL,
                    kwargs={
                        "antiepilepsy_medicine_id": antiepilepsy_medicine_DIFF_ORG.id
                    },
                )
            )

            assert (
                response.status_code == 200
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested antiepilepsy_medicine page ({URL}) of {CASE_FROM_DIFF_ORG.organisations.all()}. Has groups: {test_user.groups.all()} Expected 200 response status code, received {response.status_code}"


@pytest.mark.parametrize(
    "URL", [("edit_antiepilepsy_medicine"), ("close_antiepilepsy_medicine")]
)
@pytest.mark.django_db
def test_antiepilepsy_medicine_view_permissions_forbidden(client, URL):
    """
    Assert these users CANT view antiepilepsy_medicine for Case from different Trust.
    """

    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )
    antiepilepsy_medicine_DIFF_ORG = AntiEpilepsyMedicine.objects.create(
        management=CASE_FROM_DIFF_ORG.registration.management,
        medicine_entity=MedicineEntity.objects.get(medicine_name="Sodium valproate"),
    )

    # RCPCH AUDIT LEADS HAVE FULL ACCESS SO EXCLUDE
    users = Epilepsy12User.objects.all().exclude(first_name="RCPCH_AUDIT_LEAD")

    for test_user in users:
        client.force_login(test_user)

        # Get response object
        response = client.get(
            reverse(
                URL,
                kwargs={"antiepilepsy_medicine_id": antiepilepsy_medicine_DIFF_ORG.id},
            )
        )

        assert (
            response.status_code == 403
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested antiepilepsy_medicine page ({URL}) of case from {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"
