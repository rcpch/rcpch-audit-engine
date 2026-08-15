"""
A group of tests which have the unusual assumption that a user logged in as a lead clinician
(probably a paediatric neurologist or paediatrician with expertise in epilepsy) is using his/her credentials
(since they would have to be logged in) to subvert the audit by
opening up Postman and firing off a load of unfriendly post requests

These tests test the validations in the clean function in the epilepsy_12_user_form

[x] Assert a Lead Clinician cannot create a user in another trust
[x] Assert a Lead Clinician can create a user in the same trust
[x] Assert a Lead Clinician cannot create a user in another health board
[x] Assert a Lead Clinician cannot create a user who is an RCPCH audit team member
[x] Assert a Lead Clinician cannot create a user who is an RCPCH staff member
[x] Assert a Lead Clinician cannot create a user who is a superuser
"""

# python imports
import pytest

# django imports
from django.urls import reverse

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
    OrganisationEmployer,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)
from epilepsy12.forms_folder import Epilepsy12UserAdminCreationForm


@pytest.mark.django_db
def test_lead_clinician_cannot_create_a_user_in_another_trust(client):
    """ """

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )
    test_user.set_organisation_employer(
        organisation_employer=Organisation.objects.get(
            ods_code="RP401", trust__ods_code="RP4"
        ),
        is_primary=True,
    )

    OTHER_ORGANISATION_OTHER_TRUST = Organisation.objects.get(pk=139)  # King's

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "is_rcpch_audit_team_member": False,
        "is_rcpch_staff": False,
        "is_superuser": False,
        "email_confirmed": False,
        "is_staff": False,
        "is_child_or_carer": False,
    }
    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user)

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid() == True, "The form should be valid"

    url = reverse(
        "create_epilepsy12_user",
        kwargs={
            "organisation_id": OTHER_ORGANISATION_OTHER_TRUST.pk,
            "user_type": "organisation-staff",
        },
    )
    response = client.post(path=url, data=data)

    assert (
        response.status_code == 403
    ), "Lead clinician cannot create user in another trust"


@pytest.mark.django_db
def test_lead_clinician_can_create_a_user_in_the_same_trust(client):
    """ """

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )
    test_user.set_organisation_employer(
        organisation_employer=Organisation.objects.get(
            ods_code="RP401", trust__ods_code="RP4"
        ),
        is_primary=True,
    )

    OTHER_ORGANISATION_SAME_TRUST = Organisation.objects.get(
        pk=51
    )  # Child Development Centre - West Ham (same trust as GOS)

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "is_rcpch_audit_team_member": False,
        "is_rcpch_staff": False,
        "is_superuser": False,
        "email_confirmed": False,
        "is_staff": False,
        "is_child_or_carer": False,
    }
    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user)

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid() == True, "Valid form"

    # be sure this user does not already exist is this trust
    assert (
        OrganisationEmployer.objects.filter(
            employer_organisation=OTHER_ORGANISATION_SAME_TRUST,
            epilepsy12_user__first_name=TEMP_CREATED_USER_FIRST_NAME,
        ).exists()
        == False
    ), "User should not yet exist in the same trust"

    url = reverse(
        "create_epilepsy12_user",
        kwargs={
            "organisation_id": OTHER_ORGANISATION_SAME_TRUST.pk,
            "user_type": "organisation-staff",
        },
    )
    response = client.post(path=url, data=data, follow=True)

    assert Epilepsy12User.objects.filter(
        first_name=TEMP_CREATED_USER_FIRST_NAME,
    ).exists(), "User should be created in the same trust"
    assert OrganisationEmployer.objects.filter(
        employer_organisation=OTHER_ORGANISATION_SAME_TRUST,
        epilepsy12_user__first_name=TEMP_CREATED_USER_FIRST_NAME,
    ).exists(), "User should be created in the same trust"


@pytest.mark.django_db
def test_lead_clinician_cannot_create_a_user_in_another_local_health_board(client):
    """
    A group of tests which have the unusual assumption that a user logged in as a lead clinician
    (probably a paediatric neurologist or paediatrician with expertise in epilepsy) is using his/her credentials
    (since they would have to be logged in) to subvert the audit by
    opening up Postman and firing off a load of unfriendly post requests
    """

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    OTHER_ORGANISATION_OTHER_LOCAL_HEALTH_BOARD = Organisation.objects.get(
        ods_code="7A3LW"
    )  # Organisation in Swansea Bay University Health Board

    test_user = Epilepsy12User.objects.create(
        surname="leadclinician",
        title=1,
        email=f"welsh.leadclinician@test.com",
        role=1,
        first_name="welsh",
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
        is_superuser=False,
        email_confirmed=False,
        is_staff=False,
        is_patient_or_carer=False,
        is_active=True,
    )
    test_user.set_organisation_employer(
        Organisation.objects.get(ods_code="7A3LW"),
        is_primary=True,  # Organisation in Powys Teaching Health Board
    )

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "is_rcpch_audit_team_member": False,
        "is_rcpch_staff": False,
        "is_superuser": False,
        "email_confirmed": False,
        "is_staff": False,
        "is_patient_or_carer": False,
    }
    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user)

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid(), "Form should be valid"

    url = reverse(
        "create_epilepsy12_user",
        kwargs={
            "organisation_id": OTHER_ORGANISATION_OTHER_LOCAL_HEALTH_BOARD.pk,
            "user_type": "organisation-staff",
        },
    )
    response = client.post(path=url, data=data)

    assert (
        response.status_code == 403
    ), "User should not be able to create user in different health board"


@pytest.mark.django_db
def test_lead_clinician_can_create_a_user_in_the_same_local_health_board(client):
    """
    A group of tests which have the unusual assumption that a user logged in as a lead clinician
    (probably a paediatric neurologist or paediatrician with expertise in epilepsy) is using his/her credentials
    (since they would have to be logged in) to subvert the audit by
    opening up Postman and firing off a load of unfriendly post requests
    """

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    OTHER_ORGANISATION_SAME_LOCAL_HEALTH_BOARD = Organisation.objects.get(
        ods_code="7A6BJ",  # Chepstow Community Hospital
    )  # Chepstow Community Hospital - same Local Health Board as Ysbyty Ystrad Fawr (Aneurin Bevan Health Board)

    test_user = Epilepsy12User.objects.filter(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    ).first()

    test_user.set_organisation_employer(
        organisation_employer=Organisation.objects.get(
            ods_code="7A6AV"
        ),  # Ysbyty Ystrad Fawr - In Aneurin Bevan Health Board
        is_primary=True,
    )

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "organisation_employer": OTHER_ORGANISATION_SAME_LOCAL_HEALTH_BOARD,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "is_rcpch_audit_team_member": False,
        "is_rcpch_staff": False,
        "is_superuser": False,
        "email_confirmed": False,
        "is_staff": False,
        "is_patient_or_carer": False,
    }
    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user)

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid() == True, "Valid form"

    url = reverse(
        "create_epilepsy12_user",
        kwargs={
            "organisation_id": OTHER_ORGANISATION_SAME_LOCAL_HEALTH_BOARD.pk,
            "user_type": "organisation-staff",
        },
    )
    response = client.post(path=url, data=data, follow=True)

    assert Epilepsy12User.objects.filter(
        first_name=TEMP_CREATED_USER_FIRST_NAME,
    ).exists(), "User should be created in the same local health board"
    assert OrganisationEmployer.objects.filter(
        employer_organisation=OTHER_ORGANISATION_SAME_LOCAL_HEALTH_BOARD,
        epilepsy12_user__first_name=TEMP_CREATED_USER_FIRST_NAME,
    ).exists(), "User should be created in the same local health board"


@pytest.mark.django_db
def test_lead_clinician_cannot_create_an_RCPCH_audit_team_member(client):
    # is rcpch audit team member

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )
    test_user.set_organisation_employer(
        organisation_employer=TEST_USER_ORGANISATION, is_primary=True
    )

    OTHER_ORGANISATION_OTHER_TRUST = Organisation.objects.get(pk=139)  # King's

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "is_rcpch_audit_team_member": True,
        "is_rcpch_staff": False,
        "is_superuser": False,
        "email_confirmed": False,
        "is_staff": False,
        "is_child_or_carer": False,
    }

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid() == False, "Invalid form"

    assert (
        form.errors["is_rcpch_audit_team_member"][0]
        == f"You do not have permission to allocate RCPCH audit team member status."
    ), f"Expected {test_user} from {test_user.organisation_employer} may NOT create RCPCH Audit Team Member in {TEST_USER_ORGANISATION}"


@pytest.mark.django_db
def test_lead_clinician_cannot_create_an_RCPCH_staff_member(client):
    # is rcpch audit team member

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )

    test_user.set_organisation_employer(
        organisation_employer=TEST_USER_ORGANISATION, is_primary=True
    )

    OTHER_ORGANISATION_OTHER_TRUST = Organisation.objects.get(pk=139)  # King's

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "is_rcpch_audit_team_member": False,
        "is_rcpch_staff": True,
        "is_superuser": False,
        "email_confirmed": False,
        "is_staff": False,
        "is_child_or_carer": False,
    }

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid() == False, "Invalid form"

    assert (
        form.errors["is_rcpch_staff"][0]
        == f"You do not have permission to allocate RCPCH staff member status."
    ), f"Expected {test_user} from {test_user.organisation_employer} may NOT create RCPCH Staff Member in {TEST_USER_ORGANISATION}"


@pytest.mark.django_db
def test_lead_clinician_cannot_create_a_superuser(client):
    # is rcpch audit team member

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )

    test_user.set_organisation_employer(
        organisation_employer=TEST_USER_ORGANISATION, is_primary=True
    )

    OTHER_ORGANISATION_OTHER_TRUST = Organisation.objects.get(pk=139)  # King's

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "is_rcpch_audit_team_member": False,
        "is_rcpch_staff": False,
        "is_superuser": True,
        "email_confirmed": False,
        "is_staff": False,
        "is_child_or_carer": False,
    }

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid() == False, "Invalid form"

    assert (
        form.errors["is_superuser"][0]
        == f"You do not have permission to allocate superuser status."
    ), f"Expected {test_user} from {test_user.organisation_employer} may NOT create a superuser in {TEST_USER_ORGANISATION}"
