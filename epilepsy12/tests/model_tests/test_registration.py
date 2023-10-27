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

# Third party imports
import pytest
from django.core.exceptions import ValidationError

# RCPCH imports
from epilepsy12.models import (
    Registration,
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
        (date(2022, 11, 1), date(2024, 1, 9)),
        (date(2022, 12, 31), date(2024, 1, 9)),
        (date(2022, 1, 9), date(2023, 1, 10)),
        (date(2022, 1, 10), date(2023, 1, 10)),
        (date(2022, 1, 11), date(2024, 1, 9)),
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
        # (registration date, expected audit close date)
        (date(2022, 11, 1), date(2023, 11, 1)),
        (date(2022, 12, 31), date(2023, 12, 31)),
        (date(2022, 1, 9), date(2023, 1, 9)),
        (date(2022, 1, 10), date(2023, 1, 10)),
        (date(2022, 1, 11), date(2023, 1, 11)),
    ]

    for expected_input_output in expected_inputs_outputs:
        registration = e12_case_factory(
            registration__first_paediatric_assessment_date=expected_input_output[0]
        ).registration

        assert registration.registration_close_date == expected_input_output[1]


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

    NOTE: if `audit_submission_date` is before today, returns 0.
    """

    # submission date = 2023-01-10, 41 days after today
    registration = e12_case_factory(
        registration__first_paediatric_assessment_date=date(2022, 1, 10)
    ).registration
    assert registration.days_remaining_before_submission == 41

    # submission date = 2023-01-10, 41 days after today
    registration = e12_case_factory(
        registration__first_paediatric_assessment_date=date(2021, 1, 1)
    ).registration
    assert registration.days_remaining_before_submission == 0


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
