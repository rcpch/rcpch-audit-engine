"""
Tests the Registration model.

Cases:

    - [ ] Test a valid Registration
    - [ ] Test for DOFPA in the future
    - [ ] Test for DOFPA before E12 began
    - [ ] Test for DOFPA before the child's DOB

"""

# Standard imports
from datetime import date
from unittest.mock import patch

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import (
    Registration,
    Case,
    AuditProgress,
    KPI,
    Site,
)


@pytest.mark.django_db
def test_create_registration(registration):
    print(registration)
    print(registration.case)


@pytest.mark.django_db
def test_registration_custom_method_audit_submission_date_calculation(
    registration,
):
    """
    Tests the `audit_submission_date_calculation` accurately calculates audit submission date.

    This is always the second Tuesday of January, following 1 year after the first paediatric assessment.

    If registration date + 1 year IS the 2nd Tues of Jan, the submission date is the same as registration + 1 year.
    """

    dates = [
        # (registration date, expected audit submission date)
        (date(2022, 11, 1), date(2024, 1, 9)),
        (date(2022, 12, 31), date(2024, 1, 9)),
        (date(2022, 1, 9), date(2023, 1, 10)),
        (date(2022, 1, 10), date(2023, 1, 10)),
        (date(2022, 1, 11), date(2024, 1, 9)),
    ]

    for expected_input_output in dates:
        registration.registration_date = expected_input_output[0]
        registration.save()

        assert (
            registration.audit_submission_date == expected_input_output[1]
        )


@pytest.mark.django_db
def test_registration_custom_method_registration_date_one_year_on(
    registration,
):
    """
    Tests the `registration_date_one_year_on` accurately calculates one year on (registration close date).

    This is always 1 year after `registration_date`.
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
        registration.registration_date = expected_input_output[0]
        registration.save()

        assert (
            registration.registration_close_date
            == expected_input_output[1]
        )


@pytest.mark.django_db
def test_registration_cohort(
    registration,
):
    """
    Tests cohort number is set accurately, dependent on registration_date.

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
        registration.registration_date = expected_input_output[0]
        registration.save()

        assert registration.cohort == expected_input_output[1]


@patch.object(Registration, "get_current_date", return_value=date(2022, 11, 30))
@pytest.mark.django_db
def test_registration_days_remaining_before_submission(
    mocked_get_current_date,
    registration,
):
    """
    Tests `days_remaining_before_submission` property calculated properly.

    Calculated as submission date - current date, return number of days left days as an int.

    Test patches the example Registration instance's `.get_current_date`'s return value to always return 30 Nov 2022.

    NOTE: if `audit_submission_date` is before today, returns 0.
    """
    
    registrations = [
        
        registration(registration_date = date(2021, 1, 1)),
        
        ]
    
    
    
    # registration.registration_date=date(2022, 11, 30)

    # expected_inputs_outputs = [
    #     # (submission date, expected number of days left)
    #     (date(2022, 11, 30), 0),
    #     (date(2023, 11, 30), 365),
    #     (date(2024, 11, 30), 731),
    #     (date(2025, 11, 30), 1096),
    # ]

    # for expected_input_output in expected_inputs_outputs:
    #     registration.audit_submission_date = expected_input_output[0]
    #     registration.save()
        
    #     print(f"{registration.registration_date = }")
    #     print(f"{registration.audit_submission_date = }")
    #     diff = registration.audit_submission_date - date(2022, 11, 30)
    #     print(f"{diff =}")

    #     assert (
    #         registration.days_remaining_before_submission
    #         == expected_input_output[1]
    #     )

        
