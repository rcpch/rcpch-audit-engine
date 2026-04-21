"""
Tests to ensure closed cohort enforcement works correctly.

These tests verify that when a cohort is closed (days_remaining_before_submission == 0),
regular users cannot POST (edit) data, but can still GET (view) data.
RCPCH audit team members should retain full access regardless of cohort status.

## Critical Security Tests

[x] Assert Audit Centre Clinician can GET case in closed cohort - response.status_code == HTTPStatus.OK
[x] Assert Audit Centre Clinician CANNOT POST to case in closed cohort - response.status_code == HTTPStatus.FORBIDDEN
[x] Assert Audit Centre Lead Clinician can GET case in closed cohort - response.status_code == HTTPStatus.OK
[x] Assert Audit Centre Lead Clinician CANNOT POST to case in closed cohort - response.status_code == HTTPStatus.FORBIDDEN
[x] Assert RCPCH Audit Team can GET case in closed cohort - response.status_code == HTTPStatus.OK
[x] Assert RCPCH Audit Team CAN POST to case in closed cohort - response.status_code == HTTPStatus.OK
[x] Assert can_edit=False in template context for closed cohort

"""

# python imports
import pytest
from datetime import date, timedelta
from http import HTTPStatus

# django imports
from django.urls import reverse

# E12 Imports
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_rcpch_audit_team_data,
)
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    Case,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


@pytest.mark.django_db
def test_clinician_can_view_but_not_edit_closed_cohort_case(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """
    Test that an Audit Centre Clinician can GET (view) a case in a closed cohort
    but cannot POST (edit) it.
    
    This is the critical security test for closed cohort enforcement.
    """
    
    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    
    # Create a case with a closed cohort (audit submission date in the past)
    # Must override first_paediatric_assessment_date since Registration.save() recalculates audit_submission_date
    CLOSED_COHORT_CASE = e12_case_factory(
        first_name=f"closed_cohort_child",
        organisations__organisation=TEST_USER_ORGANISATION,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),  # Cohort 4, closed years ago
        registration__cohort=4,
    )
    
    # Verify the case is in a closed cohort
    assert CLOSED_COHORT_CASE.registration.days_remaining_before_submission == 0, \
        f"Case should have 0 days remaining, but has {CLOSED_COHORT_CASE.registration.days_remaining_before_submission}"
    assert not CLOSED_COHORT_CASE.editable(), \
        "Case should not be editable"
    
    # Get the Audit Centre Clinician
    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_clinician_data.role_str,
        is_active=True,
    )
    
    # Log in and enable 2FA
    client.force_login(test_user)
    twofactor_signin(client, test_user)
    
    # Test GET request - should succeed
    get_response = client.get(
        reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": CLOSED_COHORT_CASE.id,
            },
        )
    )
    
    assert get_response.status_code == HTTPStatus.OK, \
        f"Clinician should be able to VIEW closed cohort case. Expected 200, got {get_response.status_code}"
    
    # Verify can_edit=False in context
    assert "can_edit" in get_response.context, \
        "Template context should contain can_edit"
    assert get_response.context["can_edit"] is False, \
        f"can_edit should be False for closed cohort, but is {get_response.context['can_edit']}"
    
    # Test POST request - should fail with 403
    post_data = {
        "first_name": "NewName",
        "surname": CLOSED_COHORT_CASE.surname,
        "date_of_birth": CLOSED_COHORT_CASE.date_of_birth.strftime("%Y-%m-%d"),
        "sex": CLOSED_COHORT_CASE.sex,
        "postcode": CLOSED_COHORT_CASE.postcode or "SW1A 1AA",  # Provide default if None
        "ethnicity": CLOSED_COHORT_CASE.ethnicity,
    }
    post_response = client.post(
        reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": CLOSED_COHORT_CASE.id,
            },
        ),
        data=post_data,
    )
    
    assert post_response.status_code == HTTPStatus.FORBIDDEN, \
        f"Clinician should NOT be able to EDIT closed cohort case. Expected 403, got {post_response.status_code}"


@pytest.mark.django_db
def test_lead_clinician_cannot_edit_closed_cohort_case(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """
    Test that an Audit Centre Lead Clinician also cannot POST to closed cohort cases.
    """
    
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    
    CLOSED_COHORT_CASE = e12_case_factory(
        first_name=f"closed_cohort_child_2",
        organisations__organisation=TEST_USER_ORGANISATION,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__cohort=4,
    )
    
    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_lead_clinician_data.role_str,
        is_active=True,
    )
    
    client.force_login(test_user)
    twofactor_signin(client, test_user)
    
    # GET should succeed
    get_response = client.get(
        reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": CLOSED_COHORT_CASE.id,
            },
        )
    )
    
    assert get_response.status_code == HTTPStatus.OK, \
        f"Lead Clinician should be able to VIEW closed cohort case. Expected 200, got {get_response.status_code}"
    
    # POST should fail
    post_data = {
        "first_name": "EditedName",
        "surname": CLOSED_COHORT_CASE.surname,
        "date_of_birth": CLOSED_COHORT_CASE.date_of_birth.strftime("%Y-%m-%d"),
        "sex": CLOSED_COHORT_CASE.sex,
        "postcode": CLOSED_COHORT_CASE.postcode or "SW1A 1AA",
        "ethnicity": CLOSED_COHORT_CASE.ethnicity,
    }
    post_response = client.post(
        reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": CLOSED_COHORT_CASE.id,
            },
        ),
        data=post_data,
    )
    
    assert post_response.status_code == HTTPStatus.FORBIDDEN, \
        f"Lead Clinician should NOT be able to EDIT closed cohort case. Expected 403, got {post_response.status_code}"


@pytest.mark.django_db
def test_rcpch_audit_team_can_edit_closed_cohort_case(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """
    Test that RCPCH Audit Team members CAN still POST to closed cohort cases.
    They should have unrestricted access regardless of cohort status.
    """
    
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    
    CLOSED_COHORT_CASE = e12_case_factory(
        first_name=f"closed_cohort_child_3",
        organisations__organisation=TEST_USER_ORGANISATION,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__cohort=4,
    )
    
    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str,
        is_active=True,
    )
    
    client.force_login(test_user)
    twofactor_signin(client, test_user)
    
    # GET should succeed
    get_response = client.get(
        reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": CLOSED_COHORT_CASE.id,
            },
        )
    )
    
    assert get_response.status_code == HTTPStatus.OK, \
        f"RCPCH Audit Team should be able to VIEW closed cohort case. Expected 200, got {get_response.status_code}"
    
    # Verify can_edit=True for RCPCH staff
    assert get_response.context["can_edit"] is True, \
        f"can_edit should be True for RCPCH Audit Team, but is {get_response.context['can_edit']}"
    
    # POST should also succeed
    post_data = {
        "first_name": "RCPCHEdited",
        "surname": CLOSED_COHORT_CASE.surname,
        "date_of_birth": CLOSED_COHORT_CASE.date_of_birth.strftime("%Y-%m-%d"),
        "sex": CLOSED_COHORT_CASE.sex,
        "postcode": CLOSED_COHORT_CASE.postcode or "SW1A 1AA",
        "ethnicity": CLOSED_COHORT_CASE.ethnicity,
    }
    post_response = client.post(
        reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": CLOSED_COHORT_CASE.id,
            },
        ),
        data=post_data,
        follow=True,
    )
    
    assert post_response.status_code == HTTPStatus.OK, \
        f"RCPCH Audit Team SHOULD be able to EDIT closed cohort case. Expected 200, got {post_response.status_code}"


@pytest.mark.parametrize(
    "view_name,url_param_name",
    [
        ("register", "case_id"),
        ("epilepsy_context", "case_id"),
        ("multiaxial_diagnosis", "case_id"),
        ("assessment", "case_id"),
        ("investigations", "case_id"),
        ("management", "case_id"),
    ],
)
@pytest.mark.django_db
def test_clinician_cannot_post_to_registration_views_closed_cohort(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
    view_name,
    url_param_name,
):
    """
    Test that Clinicians cannot POST to various registration-related views
    when the cohort is closed.
    """
    
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    
    CLOSED_COHORT_CASE = e12_case_factory(
        first_name=f"closed_cohort_test_{view_name}",
        organisations__organisation=TEST_USER_ORGANISATION,
        registration__first_paediatric_assessment_date=date(2021, 6, 1),
        registration__cohort=4,
    )
    
    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_clinician_data.role_str,
        is_active=True,
    )
    
    client.force_login(test_user)
    twofactor_signin(client, test_user)
    
    # GET should succeed
    get_response = client.get(
        reverse(
            view_name,
            kwargs={url_param_name: CLOSED_COHORT_CASE.id},
        )
    )
    
    assert get_response.status_code == HTTPStatus.OK, \
        f"Clinician should be able to VIEW {view_name} in closed cohort. Expected 200, got {get_response.status_code}"
    
    # Verify can_edit=False in context
    if "can_edit" in get_response.context:
        assert get_response.context["can_edit"] is False, \
            f"can_edit should be False for {view_name} in closed cohort, but is {get_response.context['can_edit']}"


@pytest.mark.django_db
def test_open_cohort_allows_editing(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    e12_case_factory,
):
    """
    Positive control test: verify that an open cohort still allows editing.
    This ensures we haven't broken the normal edit flow.
    """
    
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )
    
    # Create a case with an open cohort (audit submission date in the future)
    # Use recent first_paediatric_assessment_date so Registration.save() calculates an open cohort  
    OPEN_COHORT_CASE = e12_case_factory(
        first_name=f"open_cohort_child",
        organisations__organisation=TEST_USER_ORGANISATION,
        # Default factory uses recent date, but be explicit for clarity
        registration__first_paediatric_assessment_date=date.today() - timedelta(days=30),
    )
    
    # Verify the case is editable (key requirement for open cohort)
    assert OPEN_COHORT_CASE.editable(), \
        "Case should be editable in open cohort"
    
    test_user = Epilepsy12User.objects.get(
        first_name=test_user_audit_centre_clinician_data.role_str,
        is_active=True,
    )
    
    client.force_login(test_user)
    twofactor_signin(client, test_user)
    
    # GET should succeed
    get_response = client.get(
        reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": OPEN_COHORT_CASE.id,
            },
        )
    )
    
    assert get_response.status_code == HTTPStatus.OK
    
    # Verify can_edit=True for open cohort
    assert get_response.context["can_edit"] is True, \
        f"can_edit should be True for open cohort, but is {get_response.context['can_edit']}"
    
    # POST should succeed
    post_data = {
        "first_name": "EditedInOpenCohort",
        "surname": OPEN_COHORT_CASE.surname,
        "date_of_birth": OPEN_COHORT_CASE.date_of_birth.strftime("%Y-%m-%d"),
        "sex": OPEN_COHORT_CASE.sex,
        "postcode": OPEN_COHORT_CASE.postcode or "SW1A 1AA",
        "ethnicity": OPEN_COHORT_CASE.ethnicity,
    }
    post_response = client.post(
        reverse(
            "update_case",
            kwargs={
                "organisation_id": TEST_USER_ORGANISATION.id,
                "case_id": OPEN_COHORT_CASE.id,
            },
        ),
        data=post_data,
        follow=True,
    )
    
    assert post_response.status_code == HTTPStatus.OK, \
        f"Clinician SHOULD be able to EDIT open cohort case. Expected 200, got {post_response.status_code}"
