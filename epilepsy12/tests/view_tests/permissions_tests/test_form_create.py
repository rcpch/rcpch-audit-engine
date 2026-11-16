"""
A group of tests which have the unusual assumption that a user logged in as a lead clinician
(probably a paediatric neurologist or paediatrician with expertise in epilepsy) is using his/her credentials
(since they would have to be logged in) to subvert the audit by
opening up Postman and firing off a load of unfriendly post requests

These tests test the validations in the clean function in the epilepsy_12_user_form

[x] Assert a Lead Clinician cannot create a user in another trust
[x] Assert a Lead Clinician can create a user in the same trust
[x] Assert a Lead Clinician cannot create a user in another health board
[x] Assert a Lead Clinician cannot promote a user to the RCPCH Audit Team role
[x] Assert a Lead Clinician cannot create a user via the RCPCH staff flow
[x] Assert a Lead Clinician cannot grant superuser status (Django admin only)
[x] Assert an RCPCH audit team member can promote a user to the RCPCH Audit Team role
[x] Assert an RCPCH audit team member can demote an RCPCH Audit Team member
"""

# python imports
import pytest

# django imports
from django.urls import reverse
from django.contrib.auth.models import Group

# E12 Imports
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    RCPCH_AUDIT_TEAM,
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
    OrganisationEmployer,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)
from epilepsy12.forms_folder import Epilepsy12UserAdminCreationForm
from epilepsy12.tests.factories import E12UserFactory


@pytest.mark.django_db
def test_lead_clinician_cannot_create_a_user_in_another_trust(client, seed_groups_fixture, seed_users_fixture):
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
def test_lead_clinician_can_create_a_user_in_the_same_trust(client, seed_groups_fixture, seed_users_fixture):
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
def test_lead_clinician_can_create_a_user_in_the_same_local_health_board(client, seed_groups_fixture, seed_users_fixture):
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
def test_lead_clinician_cannot_create_an_RCPCH_audit_team_member(client, seed_groups_fixture, seed_users_fixture):
    """
    A Lead Clinician may not promote a user to the RCPCH Audit Team role: the
    role is not offered in their choices, so even a hand-crafted POST is
    rejected by the choice validation. Promotions are reserved for RCPCH audit
    team members and superusers.
    """

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

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": RCPCH_AUDIT_TEAM,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "email_confirmed": False,
    }

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid() == False, "Invalid form"

    assert "role" in form.errors, (
        f"Expected {test_user} from {test_user.organisation_employer} may NOT create an RCPCH "
        "Audit Team member in "
        f"{TEST_USER_ORGANISATION}: the role should not be a valid choice for them"
    )


@pytest.mark.django_db
def test_lead_clinician_cannot_create_an_RCPCH_staff_member(client, seed_groups_fixture, seed_users_fixture):
    """
    The rcpch-staff create flow is reserved for RCPCH audit team members and
    superusers: a Lead Clinician firing a hand-crafted POST at it is rejected.
    """

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

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": RCPCH_AUDIT_TEAM,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "email_confirmed": False,
    }

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="rcpch-staff",
        requesting_user=test_user,
        data=data,
    )

    assert form.is_valid() == False, "Invalid form"

    assert (
        "You do not have permission to create RCPCH staff." in form.non_field_errors()
    ), f"Expected {test_user} from {test_user.organisation_employer} may NOT create RCPCH staff"


@pytest.mark.django_db
def test_lead_clinician_cannot_create_a_superuser(client, seed_groups_fixture, seed_users_fixture):
    """
    Superuser status can only be granted in the Django admin, by another
    superuser: the form has no is_superuser field, so even a hand-crafted POST
    claiming is_superuser=True is ignored.
    """

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

    data = {
        "title": 1,
        "email": f"{test_user.first_name}@test.com",
        "role": AUDIT_CENTRE_LEAD_CLINICIAN,
        "first_name": TEMP_CREATED_USER_FIRST_NAME,
        "surname": "User",
        "is_superuser": True,  # must be ignored: the form has no such field
        "email_confirmed": False,
    }

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
    )

    assert (
        "is_superuser" not in form.fields
    ), "is_superuser must not be settable through this form"

    assert form.is_valid() == True, f"Form should be valid, errors: {form.errors}"

    user = form.save()

    assert (
        user.is_superuser == False
    ), "A superuser can only be granted in the Django admin, by another superuser"


@pytest.mark.django_db
def test_rcpch_audit_team_member_can_promote_a_user_to_the_rcpch_audit_team_role(seed_groups_fixture, seed_users_fixture):
    """
    RCPCH audit team members (and superusers) may change a user's role to
    RCPCH Audit Team. The flags follow the role, so the promoted user does not
    show up as role_without_flag in audit_rcpch_user_flags.
    """

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    user_to_promote = E12UserFactory(
        email="temp_promotion_candidate@test.com",
        first_name="TEMP_PROMOTION_CANDIDATE",
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
    )

    data = {
        "title": 1,
        "email": user_to_promote.email,
        "role": RCPCH_AUDIT_TEAM,
        "first_name": user_to_promote.first_name,
        "surname": user_to_promote.surname,
        "email_confirmed": False,
    }

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="organisation-staff",
        requesting_user=test_user,
        data=data,
        instance=user_to_promote,
    )

    assert form.is_valid(), f"Form should be valid for an audit team member, errors: {form.errors}"

    promoted_user = form.save()
    promoted_user.refresh_from_db()

    assert promoted_user.role == RCPCH_AUDIT_TEAM
    assert promoted_user.is_rcpch_audit_team_member == True
    assert promoted_user.is_rcpch_staff == True


@pytest.mark.django_db
def test_rcpch_audit_team_member_can_demote_an_rcpch_audit_team_member(seed_groups_fixture, seed_users_fixture):
    """
    The reverse of a promotion is also allowed: demoting an RCPCH Audit Team
    member to an audit centre role clears the flags, so the demoted user does
    not show up as flag_without_role in audit_rcpch_user_flags.
    """

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    user_to_demote = E12UserFactory(
        email="temp_demotion_candidate@test.com",
        first_name="TEMP_DEMOTION_CANDIDATE",
        role=RCPCH_AUDIT_TEAM,
        is_rcpch_audit_team_member=True,
        is_rcpch_staff=True,
    )

    data = {
        "title": 1,
        "email": user_to_demote.email,
        "role": AUDIT_CENTRE_CLINICIAN,
        "first_name": user_to_demote.first_name,
        "surname": user_to_demote.surname,
        "email_confirmed": False,
    }

    form = Epilepsy12UserAdminCreationForm(
        rcpch_organisation="rcpch-staff",
        requesting_user=test_user,
        data=data,
        instance=user_to_demote,
    )

    assert form.is_valid(), f"Form should be valid for an audit team member, errors: {form.errors}"

    demoted_user = form.save()
    demoted_user.refresh_from_db()

    assert demoted_user.role == AUDIT_CENTRE_CLINICIAN
    assert demoted_user.is_rcpch_audit_team_member == False
    assert demoted_user.is_rcpch_staff == False
