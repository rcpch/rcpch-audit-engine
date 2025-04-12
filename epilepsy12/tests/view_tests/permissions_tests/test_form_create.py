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

    OTHER_ORGANISATION_OTHER_TRUST = Organisation.objects.get(pk=139)  # King's

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "organisation_employer": OTHER_ORGANISATION_OTHER_TRUST,
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

    assert form.is_valid() == False, "Invalid form"

    assert (
        form.errors["organisation_employer"][0]
        == f"You do not have permission to create users in different trusts or local health boards."
    ), f"Expected {test_user} from {test_user.organisation_employer} NOT to be able to create user in {OTHER_ORGANISATION_OTHER_TRUST} in different Trust"


@pytest.mark.django_db
def test_lead_clinician_can_create_a_user_in_the_same_trust(client):
    """ """

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str
    )

    OTHER_ORGANISATION_SAME_TRUST = Organisation.objects.get(
        pk=51
    )  # Child Development Centre - West Ham (same trust as GOS)

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "organisation_employer": OTHER_ORGANISATION_SAME_TRUST,
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

    assert (
        form.errors == {}
    ), f"Expected {test_user} from {test_user.organisation_employer} CAN create user in {OTHER_ORGANISATION_SAME_TRUST} in same Trust"


@pytest.mark.django_db
def test_lead_clinician_cannot_create_a_user_in_another_local_health_board(client):
    """
    A group of tests which have the unusual assumption that a user logged in as a lead clinician
    (probably a paediatric neurologist or paediatrician with expertise in epilepsy) is using his/her credentials
    (since they would have to be logged in) to subvert the audit by
    opening up Postman and firing off a load of unfriendly post requests
    """

    TEMP_CREATED_USER_FIRST_NAME = "TEMP_CREATED_USER_FIRST_NAME"

    OTHER_ORGANISATION_OTHER_LOCAL_HEALTH_BOARD = Organisation.objects.get(pk=334)

    test_user = Epilepsy12User.objects.create(
        surname="leadclinician",
        title=1,
        email=f"welsh.leadclinician@test.com",
        role=1,
        organisation_employer=Organisation.objects.get(pk=333),
        first_name="welsh",
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
        is_superuser=False,
        email_confirmed=False,
        is_staff=False,
        is_patient_or_carer=False,
    )

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "organisation_employer": OTHER_ORGANISATION_OTHER_LOCAL_HEALTH_BOARD,
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

    assert form.is_valid() == False, "Invalid form"

    assert (
        form.errors["organisation_employer"][0]
        == f"You do not have permission to create users in different trusts or local health boards."
    ), f"Expected {test_user} from {test_user.organisation_employer} NOT to be able to create user in {OTHER_ORGANISATION_OTHER_LOCAL_HEALTH_BOARD}"


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
    )  # Chepstow Community Hospital - same Local Health Board as Ysbyty Ystrad Fawr

    test_user = Epilepsy12User.objects.create(
        surname="leadclinician",
        title=1,
        email=f"welsh.leadclinician@test.com",
        role=1,
        organisation_employer=Organisation.objects.get(
            ods_code="7A6AV"
        ),  # Ysbyty Ystrad Fawr
        first_name="welsh",
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
        is_superuser=False,
        email_confirmed=False,
        is_staff=False,
        is_patient_or_carer=False,
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

    assert (
        form.errors == {}
    ), f"Expected {test_user} from {test_user.organisation_employer} CAN create user in {OTHER_ORGANISATION_SAME_LOCAL_HEALTH_BOARD} (same LHB)"


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

    OTHER_ORGANISATION_OTHER_TRUST = Organisation.objects.get(pk=139)  # King's

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "organisation_employer": TEST_USER_ORGANISATION,
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

    OTHER_ORGANISATION_OTHER_TRUST = Organisation.objects.get(pk=139)  # King's

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "organisation_employer": TEST_USER_ORGANISATION,
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

    OTHER_ORGANISATION_OTHER_TRUST = Organisation.objects.get(pk=139)  # King's

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": 1,
        "organisation_employer": TEST_USER_ORGANISATION,
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
