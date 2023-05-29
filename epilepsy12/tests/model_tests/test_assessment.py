"""
Tests the Assessment model
"""

# Standard imports
from datetime import date
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.models import Assessment, Registration


@pytest.fixture
@pytest.mark.django_db
def registration():
    """
    Creates a minimal Registration object instance for the test
    """
    return Registration.objects.create()


# The following tests check if the calculated wait times for each service are correct.
# They all use the same function (epilepsy12.general_functions.time_elapsed.stringify_time_elapsed)
# behind the scenes, so the tests are designed to cover the range of cases handled by the logic in that function.


@pytest.mark.django_db
def test_consultant_paediatrician_wait_only_one_date(db, registration):
    """
    Tests for an error when only one date is supplied
    """
    # Create an Assessment object with referral and input dates for a consultant paediatrician
    assessment = Assessment.objects.create(
        registration=registration,
        consultant_paediatrician_input_date=date(2022, 1, 10),
    )

    # Only one date was supplied so an error should be raised
    with pytest.raises(ValueError):
        assessment.consultant_paediatrician_wait()


@pytest.mark.django_db
def test_consultant_paediatrician_wait_days(db, registration):
    """
    Tests output when the wait is in days
    """
    assessment = Assessment.objects.create(
        registration=registration,
        consultant_paediatrician_referral_date=date(2022, 1, 1),
        consultant_paediatrician_input_date=date(2022, 1, 3),
    )

    # Check if the calculated wait time for the consultant paediatrician is correct
    assert assessment.consultant_paediatrician_wait() == "2 days"


@pytest.mark.django_db
def test_consultant_paediatrician_wait_weeks(db, registration):
    """
    Tests output when the wait is in weeks
    """
    assessment = Assessment.objects.create(
        registration=registration,
        consultant_paediatrician_referral_date=date(2022, 1, 1),
        consultant_paediatrician_input_date=date(2022, 1, 21),
    )

    # Check if the calculated wait time for the consultant paediatrician is correct
    assert assessment.consultant_paediatrician_wait() == "2 weeks"


@pytest.mark.django_db
def test_paediatric_neurologist_wait_months(registration):
    """
    Tests output when the wait is in months
    """
    assessment = Assessment.objects.create(
        registration=registration,
        paediatric_neurologist_referral_date=date(2022, 1, 1),
        paediatric_neurologist_input_date=date(2022, 5, 15),
    )

    # Check if the calculated wait time for the paediatric neurologist is correct
    assert assessment.paediatric_neurologist_wait() == "4 months"


@pytest.mark.django_db
def test_childrens_epilepsy_surgery_wait_years(registration):
    """
    Tests output when the wait is in years
    """
    assessment = Assessment.objects.create(
        registration=registration,
        childrens_epilepsy_surgical_service_referral_date=date(2022, 1, 1),
        childrens_epilepsy_surgical_service_input_date=date(2024, 3, 22),
    )

    # Check if the calculated wait time for the children's epilepsy surgery service is correct
    assert assessment.childrens_epilepsy_surgery_wait() == "2 years, 2 months"


@pytest.mark.django_db
def test_epilepsy_nurse_specialist_wait_same_day(registration):
    """
    Tests output when the wait in 0 days (same day)
    """
    assessment = Assessment.objects.create(
        registration=registration,
        epilepsy_specialist_nurse_referral_date=date(2022, 1, 1),
        epilepsy_specialist_nurse_input_date=date(2022, 1, 1),
    )

    # Check if the calculated wait time for the epilepsy nurse specialist is correct
    assert assessment.epilepsy_nurse_specialist_wait() == "Same day"
