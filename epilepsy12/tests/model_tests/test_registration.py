"""
Tests the Registration model.

Tests:

    - [x] Test a valid Registration
    - [x] Test for DOFPA in the future
    - [x] Test for DOFPA before E12 began
    - [x] Test for DOFPA before the child's DOB

"""

# Standard imports
from datetime import date
from dateutil.relativedelta import relativedelta
from unittest.mock import patch

# Django imports
from django.core.exceptions import ValidationError
from django.urls import reverse

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import Registration, Organisation, Epilepsy12User, Site
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_clinicial_audit_team_data,
    test_user_rcpch_audit_team_data,
)


@pytest.mark.django_db
def test_registration_custom_method_audit_submission_date_calculation(
    e12_case_factory,
):
    """
    Tests the `audit_submission_date_calculation` accurately calculates audit submission date, depending on different registration dates.

    This is always the second Tuesday of January, following 1 year after the first paediatric assessment.

    If registration date + 1 year IS the 2nd Tues of Jan, the submission date is the same as registration + 1 year.
    """

    first_paediatric_assessment_dates = [
        # (registration date, expected audit submission date)
        (date(2022, 11, 1), date(2024, 1, 9)),  # cohort 5
        (date(2022, 12, 31), date(2025, 1, 14)),  # cohort 6
        (date(2022, 1, 9), date(2024, 1, 9)),  # cohort 5
        (date(2022, 1, 10), date(2024, 1, 9)),  # cohort 5
        (date(2022, 1, 11), date(2024, 1, 9)),  # cohort 5
    ]

    for expected_input_output in first_paediatric_assessment_dates:
        registration = e12_case_factory(
            registration__first_paediatric_assessment_date=expected_input_output[0]
        ).registration

        assert registration.audit_submission_date == expected_input_output[1]


@pytest.mark.django_db
def test_registration_custom_method_first_paediatric_assessment_date_one_year_on(
    e12_case_factory,
):
    """
    Tests the `first_paediatric_assessment_date_one_year_on` accurately calculates one year on (registration close date).

    This is always 1 year after `first_paediatric_assessment_date`.
    """

    expected_inputs_outputs = [
        # (registration date, one year on date)
        (date(2022, 11, 1), date(2023, 11, 1)),  # cohort 5
        (date(2022, 12, 31), date(2023, 12, 31)),  # cohort 6
        (date(2022, 1, 9), date(2023, 1, 9)),  # cohort 5
        (date(2022, 1, 10), date(2023, 1, 10)),  # cohort 5
        (date(2022, 1, 11), date(2023, 1, 11)),  # cohort 5
    ]

    for expected_input_output in expected_inputs_outputs:
        registration = e12_case_factory(
            registration__first_paediatric_assessment_date=expected_input_output[0]
        ).registration

        assert (
            registration.completed_first_year_of_care_date == expected_input_output[1]
        )


@pytest.mark.django_db
def test_registration_cohort(
    e12_case_factory,
):
    """
    Tests cohort number is set accurately, dependent on first_paediatric_assessment_date.

    Cohorts are defined between 1st December year and 30th November in the subsequent year.

    Examples of cohort numbers:
        Cohort 4: 1 December 2020 - 30 November 2021
        Cohort 5: 1 December 2021 - 30 November 2022
        Cohort 6: 1 December 2022 - 30 November 2023
        Cohort 7: 1 December 2023 - 30 November 2024

    Dates which are too early (< 2020) should return `None`.
    """

    expected_inputs_outputs = [
        # (registration date, expected cohort)
        (date(2019, 11, 1), None),
        (date(2020, 11, 30), None),
        (date(2020, 12, 1), 4),
        (date(2021, 11, 30), 4),
        (date(2021, 12, 1), 5),
    ]

    for expected_input_output in expected_inputs_outputs:
        registration = e12_case_factory(
            registration__first_paediatric_assessment_date=expected_input_output[0]
        ).registration

        assert registration.cohort == expected_input_output[1]


@patch.object(Registration, "get_current_date", return_value=date(2022, 11, 30))
@pytest.mark.django_db
def test_registration_days_remaining_before_submission(
    mocked_get_current_date,
    e12_case_factory,
):
    """
    Tests `days_remaining_before_submission` property calculated properly.

    Calculated as submission date - current date, return number of days left days as an int.

    Test patches "today" - patches the example Registration instance's `.get_current_date`'s return value to always return 30 Nov 2022.
    """

    # submission date = 9/1/24, today = 30/11/22 405 days after today (30/11/22)
    registration = e12_case_factory(
        registration__first_paediatric_assessment_date=date(
            2022, 1, 10
        )  # cohort 5, submission date 9/1/24
    ).registration
    assert registration.days_remaining_before_submission == 406

    # submission date = 2023-01-10, 41 days after today
    registration = e12_case_factory(
        registration__first_paediatric_assessment_date=date(
            2021, 1, 1
        )  # cohort 4, submission 10/1/2023
    ).registration
    assert registration.days_remaining_before_submission == 42


@patch.object(Registration, "get_current_date", return_value=date(2025, 1, 30))
@pytest.mark.django_db
def test_registration_days_remaining_before_submission_after_submission_closed(
    mocked_get_current_date,
    e12_case_factory,
):
    # Cohort 6: 1 December 2022 - 30 November 2023: submission 14 January 2025
    registration = e12_case_factory(
        registration__first_paediatric_assessment_date=date(2023, 1, 1)
    ).registration

    # clamped to zero
    assert registration.days_remaining_before_submission == 0


@patch.object(Registration, "get_current_date", return_value=date(2025, 1, 14))
@pytest.mark.django_db
def test_registration_days_remaining_before_submission_on_last_day_of_grace_period(
    mocked_get_current_date,
    e12_case_factory,
):
    # Cohort 6: 1 December 2022 - 30 November 2023: submission 14 January 2025
    registration = e12_case_factory(
        registration__first_paediatric_assessment_date=date(2023, 1, 1)
    ).registration

    # clamped to zero
    assert registration.days_remaining_before_submission == 1


@pytest.mark.xfail
@patch.object(Registration, "get_current_date", return_value=date(2023, 1, 1))
@pytest.mark.django_db
def test_registration_validate_dofpa_not_future(
    mocked_current_date,
    e12_case_factory,
):
    """
    # TODO - add validation

    Test related to ensuring model-level validation of inputted Date of First Paediatric Assessment (first_paediatric_assessment_date).

    Patches Registration's .get_current_date() method to always be 1 Jan 2023.

    """

    # Tests that dofpa (first_paediatric_assessment_date) can't be in the future (relative to today). Tries to create and save a Registration which is 30 days ahead of today.
    future_date = Registration.get_current_date() + relativedelta(days=30)
    with pytest.raises(ValidationError):
        e12_case_factory(registration__first_paediatric_assessment_date=future_date)


@pytest.mark.xfail
@pytest.mark.django_db
def test_registration_validate_dofpa_not_before_2009(e12_case_factory):
    """
    # TODO - add validation

    Tests related to ensuring model-level validation of inputted Date of First Paediatric Assessment (first_paediatric_assessment_date).

    """

    # Tests that dofpa (first_paediatric_assessment_date) can't be before E12 began in 2009.
    with pytest.raises(ValidationError):
        e12_case_factory(
            registration__first_paediatric_assessment_date=date(2007, 8, 9)
        )


@pytest.mark.xfail
@pytest.mark.django_db
def test_registration_validate_dofpa_not_before_child_dob(e12_case_factory):
    """
    # TODO - add validation

    Tests related to ensuring model-level validation of inputted Date of First Paediatric Assessment (first_paediatric_assessment_date).

    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    # Tests that dofpa (first_paediatric_assessment_date) can't be before the child's DoB
    with pytest.raises(ValidationError):
        case = e12_case_factory(
            date_of_birth=date_of_birth,
            registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
        )


@pytest.mark.django_db
def test_accept_registration_transfer_response_not_previously_involved(
    client,
    e12_case_factory,
    e12_site_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Tests that the `transfer_response` method works as expected.

    This method is used to transfer the primary site of care to a new site.
    In the process the existing site sets the `site_is_actively_involved_in_epilepsy_care` to False and a new site is create where it is set it to True.
    If the new site is already involved in epilepsy care, the `site_is_primary_centre_of_epilepsy_care` is set to True, and the existing responsibility is retained.
    The old site is retained in the database, but is no longer the primary site of care.

    the `transfer_response` method is called from the view when the new site approves the transfer request.
    It accepts the Organisation id of the new organisation, the case id and a string indicating the response of the new organisation.
    This string can be either 'accept' or 'reject'.

    In this test, the new site (GOSH) is not already involved in epilepsy care and accepts the transfer request from KCH.
    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    KCH = Organisation.objects.get(
        ods_code="RJZ01",
        trust__ods_code="RJZ",
    )

    # Create the Case instance and associate it with the Site
    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
    )

    # Create the Site instance and set the field - KCH is the primary site of care, but a transfer to GOSH is requested
    # This means in a prior step,  KCH site_is_primary_centre_of_epilepsy_care has already been set to False and GOSH site_is_primary_centre_of_epilepsy_care has been set to True
    kch_site = e12_site_factory(
        organisation=KCH,
        case=case,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_actively_involved_in_epilepsy_care=False,
        site_is_general_paediatric_centre=False,
        site_is_childrens_epilepsy_surgery_centre=False,
        site_is_paediatric_neurology_centre=False,
    )

    # Create the Site instance and set the field - KCH is the primary site of care, but a transfer to GOSH is requested
    gos_site = e12_site_factory(
        organisation=GOSH,
        case=case,
        active_transfer=True,
        transfer_origin_organisation=KCH,
        transfer_request_date=date.today(),
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_general_paediatric_centre=False,
        site_is_childrens_epilepsy_surgery_centre=False,
        site_is_paediatric_neurology_centre=False,
    )
    case.organisations.add(KCH)
    case.registration.kpi.organisation = KCH
    case.registration.kpi.save()

    # Verify the Site instance
    assert (
        gos_site.site_is_primary_centre_of_epilepsy_care is True
    ), f"GOS has been made the primary site of care before the transfer"
    assert kch_site.case == case, f"KCH is associated with {case}"
    assert gos_site.case == case, f"GOSH is associated with {case}"
    assert gos_site.active_transfer is True, "GOS has an active transfer request"
    assert (
        gos_site.transfer_origin_organisation == KCH
    ), f"KCH has sent a transfer request to GOS, but the request has come from  {gos_site.transfer_origin_organisation}"

    # Verify the organisation associated with the KPI associated with the Case instance's registration is KCH
    assert (
        case.registration.kpi.organisation == KCH
    ), "KCH is the site associated with the KPI calculation"

    # Verify the Case instance
    case.refresh_from_db()
    assert case.organisations.filter(pk=KCH.pk).exists()

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user=test_user)

    # GOSH now approves the transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": GOSH.pk,
                "case_id": case.id,
                "organisation_response": "accept",
            },
        )
    )

    assert response.status_code == 200

    # Verify the Site instance
    kch_site = Site.objects.get(
        organisation=KCH,
        case=case,
    )

    # KCH is no longer the primary site of care
    assert kch_site.site_is_primary_centre_of_epilepsy_care is False
    assert kch_site.site_is_actively_involved_in_epilepsy_care is False
    assert kch_site.case == case

    # GOSH is now the primary site of care
    new_site = Site.objects.get(
        organisation=GOSH,
        case=case,
    )
    assert new_site.site_is_primary_centre_of_epilepsy_care is True
    assert new_site.site_is_actively_involved_in_epilepsy_care is True
    assert new_site.case == case
    assert new_site.active_transfer is False
    assert new_site.transfer_origin_organisation is None
    assert new_site.transfer_request_date is None
    # Verify the organisation associated with the KPI associated with the Case instance's registration has changed to GOSH
    assert case.registration.kpi.organisation == GOSH


@pytest.mark.django_db
def test_accept_registration_transfer_response_previously_involved(
    client,
    e12_case_factory,
    e12_site_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Tests that the `transfer_response` method works as expected.

    This method is used to transfer the primary site of care to a new site.
    In the process the existing site sets the `site_is_actively_involved_in_epilepsy_care` to False and a new site is create where it is set it to True.
    If the new site is already involved in epilepsy care, the `site_is_primary_centre_of_epilepsy_care` is set to True, and the existing responsibility is retained.
    The old site is retained in the database, but is no longer the primary site of care.

    the `transfer_response` method is called from the view when the new site approves the transfer request.
    It accepts the Organisation id of the new organisation, the case id and a string indicating the response of the new organisation.
    This string can be either 'accept' or 'reject'.

    In this test, the new site (GOSH) is already involved in epilepsy care and accepts the transfer request from KCH.
    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    KCH = Organisation.objects.get(
        ods_code="RJZ01",
        trust__ods_code="RJZ",
    )

    # Create the Case instance and associate it with the Site
    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
    )

    Site.objects.all().delete()

    # Create the Site instance and set the field - KCH is the primary site of care, but a transfer to GOSH is requested
    # This means in a prior step,  KCH site_is_primary_centre_of_epilepsy_care has already been set to False and GOSH site_is_primary_centre_of_epilepsy_care has been set to True
    #  GOSH is already involved in epilepsy care and is a general paediatric centre

    kch_site = e12_site_factory(
        organisation=KCH,
        case=case,
        site_is_general_paediatric_centre=False,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_actively_involved_in_epilepsy_care=False,
    )

    gos_site = e12_site_factory(
        active_transfer=True,
        transfer_request_date=date.today(),
        transfer_origin_organisation=KCH,
        organisation=GOSH,
        case=case,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_general_paediatric_centre=True,
        site_is_primary_centre_of_epilepsy_care=True,
    )

    case.organisations.add(
        KCH
    )  # KCH is the primary site of care making the transfer to GOSH
    case.organisations.add(
        GOSH
    )  # GOSH is already involved in epilepsy care but not the primary site of care
    case.registration.kpi.organisation = KCH
    case.registration.kpi.save()

    # Verify the Site instance
    assert (
        kch_site.site_is_primary_centre_of_epilepsy_care is False
    ), f"KCH is the primary site of care before the transfer"
    assert (
        kch_site.case == case
    ), f"The site is associated with the {case}, but should be associated with {kch_site.case}"
    assert (
        kch_site.organisation == KCH
    ), f"The site is associated with {kch_site.organisation}, but should be associated with {KCH}"
    assert (
        gos_site.active_transfer is True
    ), "GOS has an active transfer request, but the test is set up to have an active transfer"
    assert (
        gos_site.transfer_origin_organisation == KCH
    ), f"The site has a transfer request from {kch_site.transfer_origin_organisation}, but should be from {KCH}"

    assert (
        gos_site.site_is_actively_involved_in_epilepsy_care is True
    ), "GOSH is already involved in epilepsy care before transfer, but is not passing as actively involved"

    assert (
        gos_site.site_is_primary_centre_of_epilepsy_care is True
    ), "GOSH is not primary centre in epilepsy care before transfer, but is scoring as primary centre"

    assert (
        gos_site.site_is_general_paediatric_centre is True
    ), "GOSH is already involved in epilepsy care before transfer, but is not passing as general paediatric centre"

    # Verify the organisation associated with the KPI associated with the Case instance's registration is KCH
    assert (
        case.registration.kpi.organisation == KCH
    ), "KCH is the site associated with the KPI calculation"

    # Verify the Case instance
    case.refresh_from_db()
    assert case.organisations.filter(pk=KCH.pk).exists(), "KCH exists as a site"
    assert case.organisations.filter(pk=GOSH.pk).exists(), "GOSH exists as a site"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user=test_user)

    # GOSH now approves the transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": GOSH.pk,
                "case_id": case.id,
                "organisation_response": "accept",
            },
        )
    )

    assert response.status_code == 200

    # Verify the Site instance
    kch_site = Site.objects.get(
        organisation=KCH,
        case=case,
    )

    # KCH is no longer the primary site of care
    assert (
        kch_site.site_is_primary_centre_of_epilepsy_care is False
    ), "KCH is nolonger the primary site of care"
    assert (
        kch_site.site_is_actively_involved_in_epilepsy_care is False
    ), "KCH is no longer actively involved in epilepsy care"
    assert kch_site.case == case, "KCH is still historically associated with the case"

    # GOSH is now the primary site of care
    new_site = Site.objects.get(
        organisation=GOSH,
        case=case,
    )
    assert (
        new_site.site_is_primary_centre_of_epilepsy_care is True
    ), "GOSH is now the primary site of care"
    assert (
        new_site.site_is_actively_involved_in_epilepsy_care is True
    ), "GOSH is now actively involved in epilepsy care"
    assert new_site.case == case, "GOSH is associated with the case"
    assert new_site.active_transfer is False, "GOSH has no active transfer request"
    assert (
        new_site.transfer_origin_organisation is None
    ), "The transfer origin organisation has been reset to None"
    assert (
        new_site.transfer_request_date is None
    ), "The transfer request date has been reset to None"
    assert (
        new_site.site_is_general_paediatric_centre is True
    ), "GOSH remains a general paediatric centre"
    # Verify the organisation associated with the KPI associated with the Case instance's registration has changed to GOSH
    assert case.registration.kpi.organisation == GOSH


@pytest.mark.django_db
def test_accept_registration_transfer_response_transfer_centre_still_involved(
    client,
    e12_case_factory,
    e12_site_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Tests that the `transfer_response` method works as expected.

    This method is used to transfer the primary site of care to a new site.
    In the process the existing site sets the `site_is_actively_involved_in_epilepsy_care` to False and a new site is create where it is set it to True.
    If the new site is already involved in epilepsy care, the `site_is_primary_centre_of_epilepsy_care` is set to True, and the existing responsibility is retained.
    The old site is retained in the database, but is no longer the primary site of care.

    the `transfer_response` method is called from the view when the new site approves the transfer request.
    It accepts the Organisation id of the new organisation, the case id and a string indicating the response of the new organisation.
    This string can be either 'accept' or 'reject'.

    In this test, the new site (GOSH) is has no prior involvement in epilepsy care and accepts the transfer request from KCH as the lead centre.
    KCH is also the general paediatric centre and retains its involvement in epilepsy care, though it is no longer the primary site of care.

    In these circumstances, prior to the transfer, a new site is created where KCH is the primary site of care but nolonger actively involved in epilepsy care to retain the historical record.
    The existing site (KCH) is still involved in epilepsy care for general paediatrics, but is no longer the primary site of care. This means KCH has 2 sites, one as the primary site of care and one as the general paediatric centre.
    GOSH is now the primary site of care and actively involved in epilepsy care.

    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    KCH = Organisation.objects.get(
        ods_code="RJZ01",
        trust__ods_code="RJZ",
    )

    # Create the Case instance and associate it with the Site
    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
    )

    Site.objects.all().delete()

    # Create the Site instance and set the field - KCH is the primary site of care, but a transfer to GOSH is requested
    # This means in a prior step,  KCH site_is_primary_centre_of_epilepsy_care has already been set to False and GOSH site_is_primary_centre_of_epilepsy_care has been set to True
    #  GOSH is already involved in epilepsy care and is a general paediatric centre

    kch_site = e12_site_factory(
        organisation=KCH,
        case=case,
        site_is_general_paediatric_centre=True,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_actively_involved_in_epilepsy_care=True,
    )

    kch_site_old = e12_site_factory(
        organisation=KCH,
        case=case,
        site_is_general_paediatric_centre=False,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=False,
    )

    gos_site = e12_site_factory(
        active_transfer=True,
        transfer_request_date=date.today(),
        transfer_origin_organisation=KCH,
        organisation=GOSH,
        case=case,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_general_paediatric_centre=True,
        site_is_primary_centre_of_epilepsy_care=True,
    )

    case.organisations.add(
        KCH
    )  # KCH is the primary site of care making the transfer to GOSH
    case.organisations.add(
        GOSH
    )  # GOSH is already involved in epilepsy care but not the primary site of care
    case.registration.kpi.organisation = KCH
    case.registration.kpi.save()

    # Verify the Site instance
    assert (
        kch_site.site_is_primary_centre_of_epilepsy_care is False
    ), f"KCH is not the primary site of care before the transfer"
    assert kch_site.case == case, f"KCH is associated with the {case}"
    assert gos_site.active_transfer is True, "GOS has an active transfer request"
    assert (
        gos_site.transfer_origin_organisation == KCH
    ), f"GOSH has a transfer request from {kch_site.transfer_origin_organisation}, but should be from {KCH}"

    assert (
        gos_site.site_is_actively_involved_in_epilepsy_care is True
    ), "GOSH is already involved in epilepsy care before transfer"

    assert (
        gos_site.site_is_primary_centre_of_epilepsy_care is True
    ), "GOSH is primary centre in epilepsy care if approved"

    assert (
        kch_site.site_is_general_paediatric_centre is True
    ), "KCH retains involvement in epilepsy care as a general paediatric centre at the time of transfer"

    # Verify the organisation associated with the KPI associated with the Case instance's registration is KCH
    assert (
        case.registration.kpi.organisation == KCH
    ), "KCH is the site associated with the KPI calculation before transfer"

    # Verify the Case instance
    case.refresh_from_db()
    assert case.organisations.filter(pk=KCH.pk).exists(), "KCH exists as a site"
    assert case.organisations.filter(pk=GOSH.pk).exists(), "GOSH exists as a site"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user=test_user)

    # GOSH now approves the transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": GOSH.pk,
                "case_id": case.id,
                "organisation_response": "accept",
            },
        )
    )

    assert response.status_code == 200

    # Verify the Site instance of KCH still active in epilepsy care
    kch_site = Site.objects.get(
        organisation=KCH,
        case=case,
        site_is_actively_involved_in_epilepsy_care=True,
    )

    # KCH is no longer the primary site of care
    assert (
        kch_site.site_is_primary_centre_of_epilepsy_care is False
    ), "KCH is nolonger the primary site of care"
    assert kch_site.case == case, "KCH is still actively associated with the case"
    assert (
        kch_site.site_is_general_paediatric_centre is True
    ), "KCH is still a general paediatric centre"
    assert kch_site.case == case, "KCH is still a general paediatric centre"

    # GOSH is now the primary site of care
    new_site = Site.objects.get(
        organisation=GOSH,
        case=case,
    )
    old_site = Site.objects.filter(
        organisation=KCH,
        case=case,
    )
    assert (
        new_site.site_is_primary_centre_of_epilepsy_care is True
    ), "GOSH is now the primary site of care"
    assert (
        new_site.site_is_actively_involved_in_epilepsy_care is True
    ), "GOSH is now actively involved in epilepsy care"
    assert new_site.case == case, "GOSH is associated with the case"
    assert new_site.active_transfer is False, "GOSH has no active transfer request"
    assert (
        new_site.transfer_origin_organisation is None
    ), "The transfer origin organisation has been reset to None"
    assert (
        new_site.transfer_request_date is None
    ), "The transfer request date has been reset to None"
    assert (
        old_site.count() == 2
    ), "KCH has two records, one as the historical, nolonger active primary site of care, and one as the general paediatric centre"
    assert (
        old_site.filter(
            site_is_actively_involved_in_epilepsy_care=False,
            site_is_primary_centre_of_epilepsy_care=True,
        ).count()
        == 1
    ), "KCH has one historical record where it is primary site of care but nolonger actively involved in epilepsy care"
    # Verify the organisation associated with the KPI associated with the Case instance's registration has changed to GOSH
    assert case.registration.kpi.organisation == GOSH


@pytest.mark.django_db
def test_reject_registration_transfer_response_not_previously_involved(
    client,
    e12_case_factory,
    e12_site_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Tests that the `transfer_response` method works as expected.

    This method is used to transfer the primary site of care to a new site.
    In the process the existing site sets the `site_is_actively_involved_in_epilepsy_care` to False and a new site is create where it is set it to True.
    If the new site is already involved in epilepsy care, the `site_is_primary_centre_of_epilepsy_care` is set to True, and the existing responsibility is retained.
    The old site is retained in the database, but is no longer the primary site of care.

    the `transfer_response` method is called from the view when the new site approves the transfer request.
    It accepts the Organisation id of the new organisation, the case id and a string indicating the response of the new organisation.
    This string can be either 'accept' or 'reject'.

    This test is set up to test if the new site rejects the transfer request, if the new site is not already involved in the epilepsy care.
    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    KCH = Organisation.objects.get(
        ods_code="RJZ01",
        trust__ods_code="RJZ",
    )

    Site.objects.all().delete()

    # Create the Case instance and associate it with the Site
    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
    )
    # Create the Site instance and set the field - KCH is the primary site of care, but a transfer to GOSH is requested
    gos_site = e12_site_factory(
        organisation=GOSH,
        case=case,
        active_transfer=True,
        transfer_origin_organisation=KCH,
        transfer_request_date=date.today(),
    )
    case.organisations.add(KCH)
    case.registration.kpi.organisation = KCH
    case.registration.kpi.save()

    # Verify the Site instance
    assert (
        gos_site.site_is_primary_centre_of_epilepsy_care is True
    ), f"KCH is the primary site of care before the transfer, but the test is set up to transfer to {gos_site.organisation}"
    assert (
        gos_site.case == case
    ), f"The site is associated with the {case}, but should be associated with {gos_site.case}"
    assert (
        gos_site.organisation == GOSH
    ), f"The site is associated with {gos_site.organisation}, but should be associated with {GOSH}"
    assert (
        gos_site.active_transfer is True
    ), "The site has no active transfer request, but the test is set up to have an active transfer"
    assert (
        gos_site.transfer_origin_organisation == KCH
    ), f"The site has a transfer request from {gos_site.transfer_origin_organisation}, but should be from {KCH}"

    # Verify the organisation associated with the KPI associated with the Case instance's registration is KCH
    assert case.registration.kpi.organisation == KCH

    # Verify the Case instance
    case.refresh_from_db()
    assert case.organisations.filter(pk=KCH.pk).exists()

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )
    test_user.set_organisation_employer(organisation_employer=GOSH, is_primary=True)

    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user=test_user)

    # GOSH now approves the transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": GOSH.pk,
                "case_id": case.id,
                "organisation_response": "reject",
            },
        )
    )

    assert response.status_code == 200

    # Verify the Site instance
    kch_site = Site.objects.get(
        organisation=KCH,
        case=case,
    )

    # KCH is no longer the primary site of care
    assert kch_site.site_is_primary_centre_of_epilepsy_care is True
    assert kch_site.site_is_actively_involved_in_epilepsy_care is True
    assert kch_site.case == case

    # GOSH is not the primary site of care
    with pytest.raises(Site.DoesNotExist):
        Site.objects.get(
            organisation=GOSH,
            case=case,
        )

    # Verify the organisation associated with the KPI associated with the Case instance's registration has changed to GOSH
    assert case.registration.kpi.organisation == KCH


@pytest.mark.django_db
def test_reject_registration_transfer_response_previously_involved(
    client,
    e12_case_factory,
    e12_site_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Tests that the `transfer_response` method works as expected.

    This method is used to transfer the primary site of care to a new site.
    In the process the existing site sets the `site_is_actively_involved_in_epilepsy_care` to False and a new site is create where it is set it to True.
    If the new site is already involved in epilepsy care, the `site_is_primary_centre_of_epilepsy_care` is set to True, and the existing responsibility is retained.
    The old site is retained in the database, but is no longer the primary site of care.

    the `transfer_response` method is called from the view when the new site approves the transfer request.
    It accepts the Organisation id of the new organisation, the case id and a string indicating the response of the new organisation.
    This string can be either 'accept' or 'reject'.

    This test is set up to test if the new site rejects the transfer request, if the new site is not already involved in the epilepsy care.
    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    Site.objects.all().delete()

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    KCH = Organisation.objects.get(
        ods_code="RJZ01",
        trust__ods_code="RJZ",
    )

    # Create the Case instance and associate it with the Site
    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
    )
    # Create the Site instance and set the field - KCH is the primary site of care, but a transfer to GOSH is requested
    # This means in a prior step,  KCH site_is_primary_centre_of_epilepsy_care has already been set to False and GOSH site_is_primary_centre_of_epilepsy_care has been set to True
    gos_site = e12_site_factory(
        organisation=GOSH,
        case=case,
        active_transfer=True,
        transfer_origin_organisation=KCH,
        transfer_request_date=date.today(),
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_general_paediatric_centre=True,
    )

    kch_site = e12_site_factory(
        organisation=KCH,
        case=case,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=False,
    )

    case.organisations.add(
        KCH
    )  # KCH is the primary site of care making the transfer to GOSH
    case.organisations.add(GOSH)  # GOSH is already involved in epilepsy care

    case.registration.kpi.organisation = KCH  # KCH is the primary site of care
    case.registration.kpi.save()

    # Verify the Site instance
    assert (
        gos_site.site_is_primary_centre_of_epilepsy_care is True
    ), f"GOS has been set to be primary centre before transfer pending approval"
    assert gos_site.case == case, f"GOS is associated with {case}"
    assert kch_site.case == case, f"KCH is associated with {case}"
    assert (
        gos_site.active_transfer is True
    ), "GOS has no active transfer request, but the test is set up to have an active transfer"
    assert (
        gos_site.transfer_origin_organisation == KCH
    ), f"GOS has a transfer request from {gos_site.transfer_origin_organisation}, but should be from {KCH}"

    assert (
        gos_site.site_is_actively_involved_in_epilepsy_care is True
    ), "GOSH is already involved in epilepsy care before transfer"

    assert (
        gos_site.site_is_general_paediatric_centre is True
    ), "GOS is already involved in epilepsy care as a general paediatric centre before transfer"

    # Verify the organisation associated with the KPI associated with the Case instance's registration is KCH
    assert case.registration.kpi.organisation == KCH

    # Verify the Case instance
    case.refresh_from_db()
    assert case.organisations.filter(pk=KCH.pk).exists()

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user=test_user)

    # GOSH now approves the transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": GOSH.pk,
                "case_id": case.id,
                "organisation_response": "reject",
            },
        )
    )

    assert response.status_code == 200

    # Verify the Site instance
    kch_site = Site.objects.get(
        organisation=KCH,
        case=case,
    )

    # KCH is still the primary site of care
    assert kch_site.site_is_primary_centre_of_epilepsy_care is True
    assert kch_site.site_is_actively_involved_in_epilepsy_care is True
    assert kch_site.case == case

    # GOSH is not the primary site of care
    gos_site = Site.objects.get(
        organisation=GOSH,
        case=case,
    )
    assert (
        gos_site.site_is_primary_centre_of_epilepsy_care is False
    ), "GOSH is not the primary site of care"
    assert (
        gos_site.site_is_actively_involved_in_epilepsy_care is True
    ), "GOSH is still actively involved in epilepsy care"
    assert (
        gos_site.site_is_general_paediatric_centre is True
    ), "GOSH is still a general paediatric centre"

    # Verify the organisation associated with the KPI associated with the Case instance's registration has changed to GOSH
    assert case.registration.kpi.organisation == KCH, "KCH is still the primary site"


@pytest.mark.django_db
def test_reject_registration_transfer_response_transfer_centre_still_involved(
    client,
    e12_case_factory,
    e12_site_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Tests that the `transfer_response` method works as expected.

    This method is used to transfer the primary site of care to a new site.
    In the process the existing site sets the `site_is_actively_involved_in_epilepsy_care` to False and a new site is create where it is set it to True.
    If the new site is already involved in epilepsy care, the `site_is_primary_centre_of_epilepsy_care` is set to True, and the existing responsibility is retained.
    The old site is retained in the database, but is no longer the primary site of care.

    the `transfer_response` method is called from the view when the new site approves the transfer request.
    It accepts the Organisation id of the new organisation, the case id and a string indicating the response of the new organisation.
    This string can be either 'accept' or 'reject'.

    This test is set up to test if the new site rejects the transfer request, if the transfer site is previously also a general paediatric centre involved in the epilepsy care.
    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    Site.objects.all().delete()

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    KCH = Organisation.objects.get(
        ods_code="RJZ01",
        trust__ods_code="RJZ",
    )

    # Create the Case instance and associate it with the Site
    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
    )
    # Create the Site instance and set the field - KCH is the primary site of care, but a transfer to GOSH is requested
    # This means in a prior step,  KCH site_is_primary_centre_of_epilepsy_care has already been set to False and GOSH site_is_primary_centre_of_epilepsy_care has been set to True
    gos_site = e12_site_factory(
        organisation=GOSH,
        case=case,
        active_transfer=True,
        transfer_origin_organisation=KCH,
        transfer_request_date=date.today(),
        site_is_actively_involved_in_epilepsy_care=False,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_general_paediatric_centre=True,
    )

    kch_site = e12_site_factory(
        organisation=KCH,
        case=case,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_general_paediatric_centre=True,
    )

    # add a second site for KCH to test that the site is not deleted
    kch_site_old = e12_site_factory(
        organisation=KCH,
        case=case,
        site_is_actively_involved_in_epilepsy_care=False,
        site_is_primary_centre_of_epilepsy_care=True,
    )

    case.organisations.add(
        KCH
    )  # KCH is the primary site of care making the transfer to GOSH - GOSH has therefore already been made primary site of care active_transfer=True
    case.organisations.add(GOSH)

    case.registration.kpi.organisation = KCH  # KCH is the primary site of care for KPIs
    case.registration.kpi.save()

    # Verify the Site instance
    assert (
        gos_site.site_is_primary_centre_of_epilepsy_care is True
    ), f"GOS has been set to be primary centre before transfer pending approval"
    assert gos_site.case == case, f"GOS is associated with {case}"
    assert kch_site.case == case, f"KCH is associated with {case}"
    assert (
        gos_site.active_transfer is True
    ), "GOS has no active transfer request, but the test is set up to have an active transfer"
    assert (
        gos_site.transfer_origin_organisation == KCH
    ), f"GOS has a transfer request from {gos_site.transfer_origin_organisation}, but should be from {KCH}"

    assert (
        kch_site.site_is_actively_involved_in_epilepsy_care is True
    ), "KCH is actively involved in epilepsy care before transfer"

    assert (
        kch_site.site_is_general_paediatric_centre is True
    ), "KCH is involved in epilepsy care as a general paediatric centre before transfer"

    # Verify the organisation associated with the KPI associated with the Case instance's registration is KCH
    assert case.registration.kpi.organisation == KCH

    # Verify the Case instance
    case.refresh_from_db()
    assert case.organisations.filter(
        pk=KCH.pk
    ).exists(), f"KCH exists as a site for {case}"
    assert case.organisations.filter(
        pk=GOSH.pk
    ).exists(), f"KCH exists as a site for {case}"

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user=test_user)

    # GOSH now approves the transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": GOSH.pk,
                "case_id": case.id,
                "organisation_response": "reject",
            },
        )
    )

    assert response.status_code == 200

    # Verify the Site instance
    kch_sites = Site.objects.filter(
        organisation=KCH,
        case=case,
    )

    # KCH is still the primary site of care
    assert (
        kch_sites.count() == 1
    ), "KCH has reverted to one site which is both primary and actively involved in epilepsy care, as well as a general paediatric centre"
    assert kch_sites.filter(
        site_is_primary_centre_of_epilepsy_care=True
    ).exists(), "KCH is the primary site of care"
    assert kch_sites.filter(
        site_is_actively_involved_in_epilepsy_care=True
    ).exists(), "KCH is actively involved in epilepsy care"
    assert kch_sites.filter(case=case).exists(), f"KCH is still associated with {case}"

    # GOSH is not the primary site of care
    gos_site = Site.objects.get(
        organisation=GOSH,
        case=case,
    )
    assert (
        gos_site.site_is_primary_centre_of_epilepsy_care is False
    ), "GOSH is not the primary site of care"
    assert (
        gos_site.site_is_actively_involved_in_epilepsy_care is True
    ), "GOSH is still actively involved in epilepsy care"
    assert (
        gos_site.site_is_general_paediatric_centre is True
    ), "GOSH is still a general paediatric centre"

    # Verify the organisation associated with the KPI associated with the Case instance's registration has changed to GOSH
    assert case.registration.kpi.organisation == KCH, "KCH is still the primary site"
