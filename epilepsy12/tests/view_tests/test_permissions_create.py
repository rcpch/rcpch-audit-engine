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
from django.contrib.auth.models import Group

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
    # Case from DIFF Org
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    SEIZURE_ONSET_DATE = (
        CASE_FROM_SAME_ORG.registration.registration_date - relativedelta(days=7)
    )
    SEIZURE_ONSET_DATE_CONFIDENCE = "Apx"
    EPISODE_DEFINITION = "a"
    EPILEPSY_OR_NONEPILEPSY_STATUS = "E"
    EPILEPTIC_SEIZURE_ONSET_TYPE = "FO"
    FOCAL_ONSET_EPILEPSY_CHECKED_CHANGED = "LATERALITY"

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

        response = client.post(
            reverse(
                "add_episode",
                kwargs={
                    "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id
                },
            ),
            headers={"Hx-Request": "true"},
        )

        assert (
            response.status_code == HTTPStatus.OK
        ), f"{test_user} from {test_user.organisation_employer} with perms {test_user.groups.all()} request.POSTed to `add_episode` for Case from {TEST_USER_ORGANISATION}. Expected {HTTPStatus.OK}, received {response.status_code}"

        # Get new episode
        episode = Episode.objects.filter(
            multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis
        ).latest("id")

        episode_answers_data = [
            {
                "url_name": "seizure_onset_date",
                "headers": {"Hx-Trigger-Name": "seizure_onset_date"},
                "data": {"seizure_onset_date": SEIZURE_ONSET_DATE},
            },
            {
                "url_name": "seizure_onset_date_confidence",
                "headers": {"Hx-Trigger-Name": SEIZURE_ONSET_DATE_CONFIDENCE},
                "data": {},
            },
            {
                "url_name": "episode_definition",
                "headers": {"Hx-Trigger-Name": "episode_definition"},
                "data": {"episode_definition": EPISODE_DEFINITION},
            },
            {
                "url_name": "has_description_of_the_episode_or_episodes_been_gathered",
                "headers": {"Hx-Trigger-Name": "button-false"},
                "data": {},
            },
            {
                "url_name": "epilepsy_or_nonepilepsy_status",
                "headers": {"Hx-Trigger-Name": EPILEPSY_OR_NONEPILEPSY_STATUS},
                "data": {},
            },
            {
                "url_name": "epileptic_seizure_onset_type",
                "headers": {"Hx-Trigger-Name": EPILEPTIC_SEIZURE_ONSET_TYPE},
                "data": {},
            },
            {
                "url_name": "focal_onset_epilepsy_checked_changed",
                "headers": {
                    "Hx-Trigger": "focal_onset_left",
                    "Hx-Trigger-Name": FOCAL_ONSET_EPILEPSY_CHECKED_CHANGED,
                },
                "data": {},
            },
        ]

        # Fill in valid answers
        for answer in episode_answers_data:
            response = client.post(
                reverse(answer["url_name"], kwargs={"episode_id": episode.id}),
                headers={**answer["headers"], **{"Hx-Request": "true"}},
                data=answer.get("data"),
            )
            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user} from {TEST_USER_ORGANISATION} should be permitted to POST {answer['url_name']} for Case in {TEST_USER_ORGANISATION}. Expected {HTTPStatus.OK}, received {response.status_code}"

        # Reset Episode for next User
        episode = (
            Episode.objects.filter(
                multiaxial_diagnosis=CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis
            )
            .latest("id")
            .delete()
        )

        # Additional test for RCPCH_AUDIT_TEAM and CLINICAL_AUDIT_TEAM adding in different Trust
        if test_user.first_name in [
            test_user_rcpch_audit_team_data.role_str,
            test_user_clinicial_audit_team_data.role_str,
        ]:
            response = client.post(
                reverse(
                    "add_episode",
                    kwargs={
                        "multiaxial_diagnosis_id": CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis.id
                    },
                ),
                headers={"Hx-Request": "true"},
            )

            assert (
                response.status_code == HTTPStatus.OK
            ), f"{test_user} from {test_user.organisation_employer} with perms {test_user.groups.all()} request.POSTed to `add_episode` for Case from {DIFF_TRUST_DIFF_ORGANISATION}. Expected {HTTPStatus.OK}, received {response.status_code}"

            # Get new episode
            episode = Episode.objects.filter(
                multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis
            ).latest("id")

            episode_answers_data = [
                {
                    "url_name": "seizure_onset_date",
                    "headers": {"Hx-Trigger-Name": "seizure_onset_date"},
                    "data": {"seizure_onset_date": SEIZURE_ONSET_DATE},
                },
                {
                    "url_name": "seizure_onset_date_confidence",
                    "headers": {"Hx-Trigger-Name": SEIZURE_ONSET_DATE_CONFIDENCE},
                    "data": {},
                },
                {
                    "url_name": "episode_definition",
                    "headers": {"Hx-Trigger-Name": "episode_definition"},
                    "data": {"episode_definition": EPISODE_DEFINITION},
                },
                {
                    "url_name": "has_description_of_the_episode_or_episodes_been_gathered",
                    "headers": {"Hx-Trigger-Name": "button-false"},
                    "data": {},
                },
                {
                    "url_name": "epilepsy_or_nonepilepsy_status",
                    "headers": {"Hx-Trigger-Name": EPILEPSY_OR_NONEPILEPSY_STATUS},
                    "data": {},
                },
                {
                    "url_name": "epileptic_seizure_onset_type",
                    "headers": {"Hx-Trigger-Name": EPILEPTIC_SEIZURE_ONSET_TYPE},
                    "data": {},
                },
                {
                    "url_name": "focal_onset_epilepsy_checked_changed",
                    "headers": {
                        "Hx-Trigger": "focal_onset_left",
                        "Hx-Trigger-Name": FOCAL_ONSET_EPILEPSY_CHECKED_CHANGED,
                    },
                    "data": {},
                },
            ]

            # Fill in valid answers
            for answer in episode_answers_data:
                response = client.post(
                    reverse(answer["url_name"], kwargs={"episode_id": episode.id}),
                    headers={**answer["headers"], **{"Hx-Request": "true"}},
                    data=answer.get("data"),
                )
                assert (
                    response.status_code == HTTPStatus.OK
                ), f"{test_user} from {DIFF_TRUST_DIFF_ORGANISATION} should be permitted to POST {answer['url_name']} for Case in {DIFF_TRUST_DIFF_ORGANISATION}. Expected {HTTPStatus.OK}, received {response.status_code}"

            # Reset Episode for next User
            episode = (
                Episode.objects.filter(
                    multiaxial_diagnosis=CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis
                )
                .latest("id")
                .delete()
            )


# @pytest.mark.xfail(
#     reason="When an administrator tries the `add_episode` endpoint, they hit the `rcpch_403` view, specifically the htmx part. At this point, the HttpResponseClientRedirect object from django-htmx does not return a 403, instead a 200. This is an edge case, and in the UI, the add episode button is disabled."
# )
@pytest.mark.django_db
def test_add_episode_forbidden(client):
    """
    Simulating different unauthorized E12 Roles adding Episodes for Case in same Trust.

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
    # Case from DIFF Org
    CASE_FROM_DIFF_ORG = Case.objects.get(
        first_name=f"child_{DIFF_TRUST_DIFF_ORGANISATION.OrganisationName}"
    )

    users = Epilepsy12User.objects.filter(
        first_name__in=[
            f"{test_user_audit_centre_administrator_data.role_str}",
            f"{test_user_audit_centre_clinician_data.role_str}",
            f"{test_user_audit_centre_lead_clinician_data.role_str}",
        ]
    )

    if not users:
        assert False, f"No seeded users in test db. Has the test db been seeded?"

    for test_user in users:
        client.force_login(test_user)

        if test_user.first_name == test_user_audit_centre_administrator_data.role_str:
            response = client.post(
                reverse(
                    "add_episode",
                    kwargs={
                        "multiaxial_diagnosis_id": CASE_FROM_SAME_ORG.registration.multiaxialdiagnosis.id
                    },
                ),
                headers={"Hx-Request": "true"},
            )

        # Other users only forbidden from doing action in different Trust
        else:
            response = client.post(
                reverse(
                    "add_episode",
                    kwargs={
                        "multiaxial_diagnosis_id": CASE_FROM_DIFF_ORG.registration.multiaxialdiagnosis.id
                    },
                ),
                headers={"Hx-Request": "true"},
            )

        assert (
            response.status_code == HTTPStatus.FORBIDDEN
        ), f"{test_user} from {test_user.organisation_employer} with perms {test_user.groups.all()} request.POSTed to `add_episode` for Case from {TEST_USER_ORGANISATION}. Expected {HTTPStatus.FORBIDDEN}, received {response.status_code}"

