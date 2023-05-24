"""
Tests the Assessment model
"""

# Standard imports
from datetime import date
from dateutil.relativedelta import relativedelta
import pytest

# Third party imports

# RCPCH imports
from epilepsy12.models import (
    Assessment,
)

"""
- [ ] Assessment.consultant_paediatrician_referral_date and Assessment.consultant_paediatrician_input_date are both None if Assessment.consultant_paediatrician_referral_made is False
- [ ] Assessment.consultant_paediatrician_referral_date and Assessment.consultant_paediatrician_input_date cannot be in the future
- [ ] Assessment.consultant_paediatrician_referral_date cannot be after Assessment.consultant_paediatrician_input_date
- [ ] Neither Assessment.consultant_paediatrician_referral_date nor Assessment.consultant_paediatrician_input_date can be before Registration.registration_date or Case.date_of_birth
- [ ] Assessment.paediatric_neurologist_input_date and Assessment.paediatric_neurologist_referral_date are both None if Assessment.paediatric_neurologist_referral_made is False
- [ ] Assessment.paediatric_neurologist_input_date and Assessment.paediatric_neurologist_referral_date cannot be in the future
- [ ] Assessment.paediatric_neurologist_input_date cannot be after Assessment.paediatric_neurologist_referral_date
- [ ] Neither Assessment.paediatric_neurologist_input_date nor Assessment.paediatric_neurologist_referral_date can be before Registration.registration_date or Case.date_of_birth
- [ ] Assessment.childrens_epilepsy_surgical_service_input_date and Assessment.childrens_epilepsy_surgical_service_referral_date are both None if Assessment.childrens_epilepsy_surgical_service_referral_made is False
- [ ] Assessment.childrens_epilepsy_surgical_service_input_date and Assessment.childrens_epilepsy_surgical_service_referral_date cannot be in the future
- [ ] Assessment.childrens_epilepsy_surgical_service_input_date cannot be after Assessment.childrens_epilepsy_surgical_service_referral_date
- [ ] Neither Assessment.childrens_epilepsy_surgical_service_input_date nor Assessment.childrens_epilepsy_surgical_service_referral_date can be before Registration.registration_date or Case.date_of_birth
- [ ] Assessment.epilepsy_specialist_nurse_input_date and Assessment.epilepsy_specialist_nurse_referral_date are both None if Assessment.epilepsy_specialist_nurse_referral_made is False
- [ ] Assessment.epilepsy_specialist_nurse_input_date and Assessment.epilepsy_specialist_nurse_referral_date cannot be in the future
- [ ] Assessment.epilepsy_specialist_nurse_input_date cannot be after Assessment.epilepsy_specialist_nurse_referral_date
- [ ] Neither Assessment.epilepsy_specialist_nurse_input_date nor Assessment.epilepsy_specialist_nurse_referral_date can be before Registration.registration_date or Case.date_of_birth
"""


# The following tests check if the calculated wait times for each service are correct.
# They all use the same function (epilepsy12.general_functions.time_elapsed.stringify_time_elapsed)
# behind the scenes, so the tests are designed to cover the range of cases handled by the logic in that function.

@pytest.mark.xfail
@pytest.mark.django_db
def test_consultant_paediatrician_wait_only_one_date(
    e12_case_factory
):
    """
    Tests for an error when only one date is supplied
    """
    # Create an Assessment object with referral and input dates for a consultant paediatrician
    assessment = e12_case_factory(
            registration__assessment__consultant_paediatrician_input_date = None
        ).registration.assessment
    
    # Only one date was supplied so an error should be raised
    with pytest.raises(ValueError):
        assessment.consultant_paediatrician_wait()


@pytest.mark.django_db
def test_consultant_paediatrician_wait_days(
    e12_case_factory
):
    """
    Tests output when the wait is in days
    """
    assessment = e12_case_factory(
            registration__assessment__consultant_paediatrician_referral_date = date(2023,1,1),
            registration__assessment__consultant_paediatrician_input_date = date(2023,1,3),
        ).registration.assessment

    # Check if the calculated wait time for the consultant paediatrician is correct
    assert assessment.consultant_paediatrician_wait() == "2 days"


@pytest.mark.django_db
def test_consultant_paediatrician_wait_weeks(
    e12_case_factory
):
    """
    Tests output when the wait is in weeks
    """
    referral_date = date(2023,1,1)
    input_date = referral_date + relativedelta(weeks=2)
    
    assessment = e12_case_factory(
            registration__assessment__consultant_paediatrician_referral_date = referral_date,
            registration__assessment__consultant_paediatrician_input_date = input_date,
        ).registration.assessment

    # Check if the calculated wait time for the consultant paediatrician is correct
    assert assessment.consultant_paediatrician_wait() == "2 weeks"


@pytest.mark.django_db
def test_paediatric_neurologist_wait_months(
    e12_case_factory
):
    """
    Tests output when the wait is in months
    """
    referral_date = date(2023,1,1)
    input_date = referral_date + relativedelta(months=4)
    
    assessment = e12_case_factory(
            registration__assessment__paediatric_neurologist_referral_date = referral_date,
            registration__assessment__paediatric_neurologist_input_date = input_date,
        ).registration.assessment

    # Check if the calculated wait time for the paediatric neurologist is correct
    assert assessment.paediatric_neurologist_wait() == "4 months"


@pytest.mark.django_db
def test_childrens_epilepsy_surgery_wait_years(
    e12_case_factory
):
    """
    Tests output when the wait is in years
    """
    referral_date = date(2023,1,1)
    input_date = referral_date + relativedelta(years=2, months=2)
    
    assessment = e12_case_factory(
            registration__assessment__childrens_epilepsy_surgical_service_referral_date = referral_date,
            registration__assessment__childrens_epilepsy_surgical_service_input_date = input_date,
        ).registration.assessment

    # Check if the calculated wait time for the children's epilepsy surgery service is correct
    assert assessment.childrens_epilepsy_surgery_wait() == "2 years, 2 months"


@pytest.mark.django_db
def test_epilepsy_nurse_specialist_wait_same_day(
    e12_case_factory
):
    """
    Tests output when the wait is in 0 days (same day)
    """
    referral_date = date(2023,1,1)
    input_date = referral_date
    
    assessment = e12_case_factory(
            registration__assessment__epilepsy_specialist_nurse_referral_date = referral_date,
            registration__assessment__epilepsy_specialist_nurse_input_date = input_date,
        ).registration.assessment

    # Check if the calculated wait time for the epilepsy nurse specialist is correct
    assert assessment.epilepsy_nurse_specialist_wait() == "Same day"

