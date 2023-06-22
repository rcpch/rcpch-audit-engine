"""

## Create Tests

    [x] Assert an Audit Centre Lead Clinician can create users inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can create users nationally, inside own Trust, and outside  - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can create users nationally, inside own Trust, and outside  - response.status_code == HTTPStatus.OK

    [x] Assert an Audit Centre Administrator CANNOT create users - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT create users - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT create users outside own Trust - response.status_code == HTTPStatus.FORBIDDEN


    [x] Assert an Audit Centre Administrator can create patients inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Clinician can create patients inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert an Audit Centre Lead Clinician can create patients inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can create patients  inside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can create patients  inside own Trust  - response.status_code == HTTPStatus.OK
    [x] Assert RCPCH Audit Team can create patients  outside own Trust - response.status_code == HTTPStatus.OK
    [x] Assert Clinical Audit Team can create patients  outside own Trust - response.status_code == HTTPStatus.OK

    [x] Assert an Audit Centre Administrator CANNOT create patients outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an audit centre clinician CANNOT create patients outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [x] Assert an Audit Centre Lead Clinician CANNOT create patients outside own Trust - response.status_code == HTTPStatus.FORBIDDEN


    [ ] Assert an Audit Centre Clinician can create patient records inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert an Audit Centre Lead Clinician can create patient records inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can create patient records nationally, inside own Trust, and outside  - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can create patient records nationally, inside own Trust, and outside  - response.status_code == HTTPStatus.OK

    [ ] Assert an Audit Centre Administrator CANNOT create patient records - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an audit centre clinician CANNOT create patient records outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Lead Clinician CANNOT create patient records outside own Trust - response.status_code == HTTPStatus.FORBIDDEN



# Episode

    [ ] Assert an Audit Centre Clinician can 'add_episode' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert an Audit Centre Lead Clinician can 'add_episode' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can 'add_episode' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can 'add_episode' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can 'add_episode' inside different Trust - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can 'add_episode' inside different Trust - response.status_code == HTTPStatus.OK
    
    [ ] Assert an Audit Centre Administrator CANNOT 'add_episode' - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Clinician CANNOT 'add_episode' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_episode' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN

# Comorbidity

    [ ] Assert an Audit Centre Clinician can 'add_comorbidity' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert an Audit Centre Lead Clinician can 'add_comorbidity' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can 'add_comorbidity' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can 'add_comorbidity' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can 'add_comorbidity' inside different Trust - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can 'add_comorbidity' inside different Trust - response.status_code == HTTPStatus.OK
    
    [ ] Assert an Audit Centre Administrator CANNOT 'add_comorbidity' - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Clinician CANNOT 'add_comorbidity' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_comorbidity' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN

# Syndrome

    [ ] Assert an Audit Centre Clinician can 'add_syndrome' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert an Audit Centre Lead Clinician can 'add_syndrome' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can 'add_syndrome' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can 'add_syndrome' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can 'add_syndrome' inside different Trust - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can 'add_syndrome' inside different Trust - response.status_code == HTTPStatus.OK
    
    [ ] Assert an Audit Centre Administrator CANNOT 'add_syndrome' - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Clinician CANNOT 'add_syndrome' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_syndrome' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN


# Antiepilepsy Medicine

    [ ] Assert an Audit Centre Clinician can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert an Audit Centre Lead Clinician can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can 'add_antiepilepsy_medicine' inside own Trust - response.status_code == HTTPStatus.OK
    [ ] Assert RCPCH Audit Team can 'add_antiepilepsy_medicine' inside different Trust - response.status_code == HTTPStatus.OK
    [ ] Assert Clinical Audit Team can 'add_antiepilepsy_medicine' inside different Trust - response.status_code == HTTPStatus.OK
    
    [ ] Assert an Audit Centre Administrator CANNOT 'add_antiepilepsy_medicine' - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Clinician CANNOT 'add_antiepilepsy_medicine' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_antiepilepsy_medicine' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
"""

# python imports
import pytest
from http import HTTPStatus
from datetime import date
from dateutil.relativedelta import relativedelta

# django imports
from django.urls import reverse
from django.db import transaction

# E12 Imports
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
    Episode,
    Syndrome,
    Comorbidity,
    ComorbidityEntity,
    AntiEpilepsyMedicine,
    MedicineEntity,
)
from epilepsy12.forms import (
    Epilepsy12UserAdminCreationForm,
)
from epilepsy12.constants import (
    VALID_NHS_NUMS,
)


@pytest.mark.django_db
def test_user_create_same_org_success(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,
):
    """Integration test checking functionality of view and form.

    Simulating different E12 users with different roles attempting to create Users inside own trust.

    Additionally, RCPCH Audit Team and Clinical Audit Team roles should be able to create user in different trust.
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    users = Epilepsy12User.objects.all().exclude(
        first_name__in=["AUDIT_CENTRE_ADMINISTRATOR", "AUDIT_CENTRE_CLINICIAN"]
    )

    if not users:
        assert False, f"No seeded users in test db. Has the test db been seeded?"

    for test_user in users:
        client.force_login(test_user)

        url = reverse(
            "create_epilepsy12_user",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "user_type": "organisation-staff",
            },
        )

        response = client.get(url)

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` of {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected 200 response status code, received {response.status_code}"

        data = {
            "title": 1,
            "email": f"{test_user.first_name}@test.com",
            "role": 1,
            "organisation_employer": TEST_USER_ORGANISATION.id,
            "first_name": TEMP_CREATED_USER_FIRST_NAME,
            "surname": "User",
            "is_rcpch_audit_team_member": True,
            "is_rcpch_staff": False,
            "email_confirmed": True,
        }

        response = client.post(url, data=data)

        # This is valid form data, should redirect
        assert (
            response.status_code == HTTPStatus.FOUND
        ), f"Valid E12User form data POSTed by {test_user}, expected status_code 302, received {response.status_code}"

    assert (
        Epilepsy12User.objects.filter(first_name=TEMP_CREATED_USER_FIRST_NAME).count()
        == 3
    ), f"Logged in as 3 different people and created an e12 user with first_name = {TEMP_CREATED_USER_FIRST_NAME}. Should be 3 matches in db for this filter."


@pytest.mark.django_db
def test_user_create_diff_org_success(
    client,
):
    """Integration test checking functionality of view and form.

    RCPCH Audit Team and Clinical Audit Team roles should be able to create user in different trust.
    """

    # set up constants

    # ADDENBROOKE'S
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    users = Epilepsy12User.objects.filter(
        first_name__in=["RCPCH_AUDIT_TEAM", "CLINICAL_AUDIT_TEAM"]
    )

    if not users:
        assert False, f"No seeded users in test db. Has the test db been seeded?"

    for test_user in users:
        client.force_login(test_user)

        url = reverse(
            "create_epilepsy12_user",
            kwargs={
                "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                "user_type": "organisation-staff",
            },
        )

        data = {
            "title": 1,
            "email": f"{test_user.first_name}@test.com",
            "role": 1,
            "organisation_employer": DIFF_TRUST_DIFF_ORGANISATION.id,
            "first_name": TEMP_CREATED_USER_FIRST_NAME,
            "surname": "User",
            "is_rcpch_audit_team_member": True,
            "is_rcpch_staff": False,
            "email_confirmed": True,
        }

        response = client.post(url, data=data)

        # This is valid form data, should redirect
        assert (
            response.status_code == HTTPStatus.FOUND
        ), f"Valid E12User form data POSTed by {test_user}, expected status_code 302, received {response.status_code}"

    assert (
        Epilepsy12User.objects.filter(first_name=TEMP_CREATED_USER_FIRST_NAME).count()
        == 2
    ), f"Logged in as 2 different people and created an e12 user with first_name = {TEMP_CREATED_USER_FIRST_NAME}. Should be 2 matches in db for this filter."


@pytest.mark.django_db
def test_user_creation_forbidden(
    client,
):
    """Integration test checking functionality of view and form.

    Simulating unpermitted E12 users attempting to create Users inside own trust.

    Additionally, AUDIT_CENTRE_LEAD_CLINICIAN role CANNOT create user in different trust.
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

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    users = Epilepsy12User.objects.filter(
        first_name__in=[
            "AUDIT_CENTRE_ADMINISTRATOR",
            "AUDIT_CENTRE_CLINICIAN",
            "AUDIT_CENTRE_LEAD_CLINICIAN",
        ]
    )

    if not users:
        assert False, f"No seeded users in test db. Has the test db been seeded?"

    for test_user in users:
        client.force_login(test_user)

        url = reverse(
            "create_epilepsy12_user",
            kwargs={
                "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                "user_type": "organisation-staff",
            },
        )

        response = client.get(url)

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.FORBIDDEN} response status code, received {response.status_code}"

        data = {
            "title": 1,
            "email": f"{test_user.first_name}@test.com",
            "role": 1,
            "organisation_employer": DIFF_TRUST_DIFF_ORGANISATION.id,
            "first_name": TEMP_CREATED_USER_FIRST_NAME,
            "surname": "User",
            "is_rcpch_audit_team_member": True,
            "is_rcpch_staff": False,
            "email_confirmed": True,
        }

        response = client.post(url, data=data)

        # This is valid form data, should redirect
        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"Unpermitted E12User {test_user} attempted to create an E12User. expected status_code {HTTPStatus.FORBIDDEN}, received {response.status_code}"

    assert (
        Epilepsy12User.objects.filter(first_name=TEMP_CREATED_USER_FIRST_NAME).count()
        == 0
    ), f"Logged in as 3 different unpermitted Users and attempted to create an e12 user with first_name = {TEMP_CREATED_USER_FIRST_NAME}. Should be 0 matches in db for this filter."


@pytest.mark.django_db
def test_patient_create_success(
    client,
):
    """Integration test checking functionality of view and form.

    Simulating different E12 users with different roles attempting to create Patients inside own trust.
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

    TEST_FIRST_NAME = "TEST_FIRST_NAME"

    users = Epilepsy12User.objects.all()

    if not users:
        assert False, f"No seeded users in test db. Has the test db been seeded?"

    for test_user in users:
        client.force_login(test_user)

        url = reverse(
            "create_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
            },
        )

        response = client.get(url)

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` of {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected 200 response status code, received {response.status_code}"

        data = {
            "first_name": TEST_FIRST_NAME,
            "surname": "Chandran",
            "date_of_birth": date(2023, 6, 15),
            "sex": "1",
            "nhs_number": "400 0000 012",
            "postcode": "SW1A 1AA",
            "ethnicity": "N",
        }

        response = client.post(url, data=data)

        # This is valid form data, should redirect
        assert (
            response.status_code == HTTPStatus.FOUND
        ), f"Valid Case form data POSTed by {test_user}, expected status_code 302, received {response.status_code}"

        assert Case.objects.filter(
            first_name=TEST_FIRST_NAME
        ).exists(), f"Logged in as {test_user} and created Case at {url}. Created Case not found in db."

        # Remove Case for next user
        Case.objects.filter(first_name=TEST_FIRST_NAME).delete()

        # Additionally RCPCH_AUDIT_TEAM and CLINICAL_AUDIT_TEAM can create Case in different Trust
        if test_user.first_name in [
            test_user_rcpch_audit_team_data.role_str,
            test_user_clinicial_audit_team_data.role_str,
        ]:
            url = reverse(
                "create_case",
                kwargs={
                    "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                },
            )

            response = client.get(url)

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected 200 response status code, received {response.status_code}"

            data = {
                "first_name": TEST_FIRST_NAME,
                "surname": "Chandran",
                "date_of_birth": date(2023, 6, 15),
                "sex": "1",
                "nhs_number": "400 0000 012",
                "postcode": "SW1A 1AA",
                "ethnicity": "N",
            }

            response = client.post(url, data=data)

            # This is valid form data, should redirect
            assert (
                response.status_code == HTTPStatus.FOUND
            ), f"Valid Case form data POSTed by {test_user}, expected status_code 302, received {response.status_code}"

            assert Case.objects.filter(
                first_name=TEST_FIRST_NAME
            ).exists(), f"Logged in as {test_user} and created Case at {url}. Created Case not found in db."

            # Remove Case for next user
            Case.objects.filter(first_name=TEST_FIRST_NAME).delete()


@pytest.mark.django_db
def test_patient_creation_forbidden(
    client,
):
    """Integration test checking functionality of view and form.

    Simulating unpermitted E12 Users attempting to create patients.

    Additionally, AUDIT_CENTRE_LEAD_CLINICIAN role only NOT ALLOWED to create patient in different trust.
    """

    # set up constants

    # ADDENBROOKE'S
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    TEST_FIRST_NAME = "TEST_FIRST_NAME"

    users = Epilepsy12User.objects.filter(
        first_name__in=[
            "AUDIT_CENTRE_ADMINISTRATOR",
            "AUDIT_CENTRE_CLINICIAN",
            "AUDIT_CENTRE_LEAD_CLINICIAN",
        ]
    )

    if not users:
        assert False, f"No seeded users in test db. Has the test db been seeded?"

    for test_user in users:
        client.force_login(test_user)

        url = reverse(
            "create_case",
            kwargs={
                "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
            },
        )

        response = client.get(url)

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested `{url}` of {DIFF_TRUST_DIFF_ORGANISATION}. Has groups: {test_user.groups.all()}. Expected {HTTPStatus.FORBIDDEN} status code, received {response.status_code}"

        data = {
            "first_name": TEST_FIRST_NAME,
            "surname": "Chandran",
            "date_of_birth": date(2023, 6, 15),
            "sex": "1",
            "nhs_number": "400 0000 012",
            "postcode": "SW1A 1AA",
            "ethnicity": "N",
        }

        response = client.post(url, data=data)

        # This is valid form data but should be forbidden
        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"Valid Case form data POSTed by unpermitted {test_user}, expected status_code {HTTPStatus.FORBIDDEN}, received {response.status_code}"

        assert not Case.objects.filter(
            first_name=TEST_FIRST_NAME
        ).exists(), f"Logged in as {test_user} and attempted to Case at {url}. Unpermitted so Case should not be created."


@pytest.mark.django_db
def test_add_episode_success(client):
    """
    Simulating different permitted E12 Roles adding 1 valid Episode.

    Additionally, RCPCH_AUDIT_TEAM and CLINICAL_AUDIT_TEAM can add Episode in different Trust.
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

    # Case from SAME Org
    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    TEST_FIRST_NAME = "TEST_FIRST_NAME"
    SEIZURE_ONSET_DATE = (
        CASE_FROM_SAME_ORG.registration.registration_date - relativedelta(days=7)
    )
    SEIZURE_ONSET_DATE_CONFIDENCE = 'Apx'
    EPISODE_DEFINITION='a'
    HAS_DESCRIPTION_OF_EPISODE_BEEN_GATHERED = False
    EPILEPSY_OR_NONEPILEPSY_STATUS='E'
    EPILEPTIC_SEIZURE_ONSET_TYPE='FO'
    FOCAL_ONSET_EPILEPSY_CHECKED_CHANGED='LATERALITY'

    users = Epilepsy12User.objects.filter(
        first_name__in=[
            # f"{test_user_audit_centre_administrator_data.role_str}",
            f"{test_user_audit_centre_clinician_data.role_str}",
            f"{test_user_audit_centre_lead_clinician_data.role_str}",
            f"{test_user_clinicial_audit_team_data.role_str}",
            f"{test_user_rcpch_audit_team_data.role_str}",
        ]
    )

    if not users:
        assert False, f"No seeded users in test db. Has the test db been seeded?"

    for test_user in users:
        client.force_login(test_user)

        client.post(
            reverse(
                "add_episode",
                kwargs={
                    "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id
                },
            ),
            headers={"Hx-Request": "true"},
        )

        # Ensure a new episode was added
        assert (
            Episode.objects.filter(
                multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis
            ).count()
            == 2
        ), f"{test_user} POST requested url='add_episode' but new Episode not added to test db."

        # Get new episode
        episode = Episode.objects.filter(
            multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis
        ).latest("id")

        # Fill in valid answers
        client.post(
            reverse(
                "seizure_onset_date",
                kwargs={"episode_id": episode.id},
            ),
            headers={"Hx-Trigger-Name": "seizure_onset_date", "Hx-Request": "true"},
            data={"seizure_onset_date": SEIZURE_ONSET_DATE},
        )
        client.post(
            reverse(
                "seizure_onset_date_confidence",
                kwargs={"episode_id": episode.id},
            ),
            headers={"Hx-Trigger-Name": SEIZURE_ONSET_DATE_CONFIDENCE, "Hx-Request": "true"},
        )
        client.post(
            reverse(
                "episode_definition",
                kwargs={"episode_id": episode.id},
            ),
            headers={"Hx-Trigger-Name": "episode_definition", "Hx-Request": "true"},
            data={'episode_definition':EPISODE_DEFINITION}
        )
        client.post(
            reverse(
                "has_description_of_the_episode_or_episodes_been_gathered",
                kwargs={"episode_id": episode.id},
            ),
            headers={"Hx-Trigger-Name": 'button-false', "Hx-Request": "true"},
        )
        client.post(
            reverse(
                "epilepsy_or_nonepilepsy_status",
                kwargs={"episode_id": episode.id},
            ),
            headers={"Hx-Trigger-Name": EPILEPSY_OR_NONEPILEPSY_STATUS, "Hx-Request": "true"},
        )
        client.post(
            reverse(
                "epileptic_seizure_onset_type",
                kwargs={"episode_id": episode.id},
            ),
            headers={"Hx-Trigger-Name": EPILEPTIC_SEIZURE_ONSET_TYPE, "Hx-Request": "true"},
        )
        client.post(
            reverse(
                "focal_onset_epilepsy_checked_changed",
                kwargs={"episode_id": episode.id},
            ),
            headers={"Hx-Trigger":'focal_onset_left',"Hx-Trigger-Name": FOCAL_ONSET_EPILEPSY_CHECKED_CHANGED, "Hx-Request": "true"},
        )

        episode = Episode.objects.filter(
            multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis
        ).latest("id")
        
        assert episode.seizure_onset_date == SEIZURE_ONSET_DATE
        assert episode.seizure_onset_date_confidence == SEIZURE_ONSET_DATE_CONFIDENCE
        assert episode.episode_definition == EPISODE_DEFINITION
        assert episode.has_description_of_the_episode_or_episodes_been_gathered == HAS_DESCRIPTION_OF_EPISODE_BEEN_GATHERED 
        assert episode.epilepsy_or_nonepilepsy_status == EPILEPSY_OR_NONEPILEPSY_STATUS
        assert episode.epileptic_seizure_onset_type == EPILEPTIC_SEIZURE_ONSET_TYPE
        assert episode.focal_onset_left == True
        

        # Reset Episode for next User
        episode.delete()


@pytest.mark.django_db
def test_add_episode_forbidden(client):
    """
    Simulating different permitted E12 Roles adding Episodes for Case in same Trust.



    [ ] Assert an Audit Centre Administrator CANNOT 'add_episode' - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Clinician CANNOT 'add_episode' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN
    [ ] Assert an Audit Centre Lead Clinician CANNOT 'add_episode' outside own Trust - response.status_code == HTTPStatus.FORBIDDEN

    """
    pass
