"""
Tests the Investigations model.

Tests:
- [ ] Investigations.eeg_request_date # TODO what should go here?
= [x] Investigations.eeg_performed_date should be None if Investigations.eeg_indicated is False or None
- [x] Investigations.eeg_request_date cannot be after Investigations.eeg_performed_date
- [x] Investigations.eeg_request_date cannot be before Registration.registration_date
- [x] Neither Investigations.eeg_request_date nor Investigations.eeg_performed_date can be in the future
- [x] Investigations.mri_brain_requested_date Investigations.mri_brain_reported_date should be None if Investigations.mri_indicated is False or None
- [x] Investigations.mri_brain_requested_date cannot be after Investigations.mri_brain_reported_date
- [x] Investigations.mri_brain_requested_date cannot be before Registration.registration_date
- [x] Neither Investigations.mri_brain_requested_date nor Investigations.mri_brain_reported_date can be in the future
- [x] Investigations.mri_wait is only calculated if both Investigations.mri_brain_requested_date and Investigations.mri_brain_reported_date are present and valid (including MRI declined date not set)
- [x] Investigations.mri_wait is only calculated if both Investigations.eeg_request_date and Investigations.eeg_performed_date are present and valid (including EEG declined date not set)

"""

# Standard imports
from datetime import date
from dateutil.relativedelta import relativedelta
from unittest.mock import patch

# Third party imports
import pytest
from django.core.exceptions import ValidationError

# RCPCH imports
from epilepsy12.models import Investigations


@pytest.mark.xfail
@pytest.mark.django_db
def test_validation_no_performed_date_when_not_indicated(
    e12_case_factory,
):
    """Tests:
    - Investigations.eeg_performed_date should be None if Investigations.eeg_indicated is False or None
    - Investigations.mri_brain_requested_date Investigations.mri_brain_reported_date should be None if Investigations.mri_indicated is False or None
    """
    
    performed_date = date(2023,10,1)
    
    with pytest.raises(ValidationError):
        # Create an Investigations object where eeg_indicated = False, and related fields None, then .eeg_performed_date to a date, attempts to save it.
        e12_case_factory(
            registration__investigations__eeg_not_requested = True,
            registration__investigations__eeg_performed_date = performed_date
        )
    with pytest.raises(ValidationError):
        # Create an Investigations object where mri_brain_indicated = False, and related fields None, then .mri_brain_reported_date to a date, attempts to save it.
        e12_case_factory(
            registration__investigations__mri_brain_not_requested = True,
            registration__investigations__mri_brain_reported_date = performed_date
        )
    
    
@pytest.mark.xfail
@pytest.mark.django_db
def test_validation_request_date_cant_be_after_performed_date(
    e12_case_factory,
):
    """Tests:
    - Investigations.eeg_request_date cannot be after Investigations.eeg_performed_date
    - Investigations.mri_brain_requested_date cannot be after Investigations.mri_brain_reported_date
    """
    
    request_date = date(2023,2,1)
    performed_date = date(2023,1,1)
    
    with pytest.raises(ValidationError):
        # Create an Investigations object where request date is after performed date
        e12_case_factory(
            registration__investigations__eeg_request_date = request_date,
            registration__investigations__eeg_performed_date = performed_date,
        )
    with pytest.raises(ValidationError):
        # Create an Investigations object where request date is after performed date
        e12_case_factory(
            registration__investigations__mri_brain_requested_date_request_date = request_date,
            registration__investigations__mri_brain_reported_date_performed_date = performed_date,
        )

@pytest.mark.xfail    
@pytest.mark.django_db
def test_validation_request_date_cant_be_before_registration(
    e12_case_factory,
):
    """Tests:
    - Investigations.eeg_request_date cannot be before Registration.registration_date
    - Investigations.mri_brain_requested_date cannot be before Registration.registration_date
    """
    
    # assign request date to 10 days before registration
    registration_date = date(2023,1,1)
    request_date = registration_date - relativedelta(days=10)
    
    with pytest.raises(ValidationError):
        # Create an Investigations object where request date is after performed date
        case = e12_case_factory(
            registration__registration_date = registration_date,
            registration__investigations__eeg_request_date = request_date,
        )

    with pytest.raises(ValidationError):
        # Create an Investigations object where request date is after performed date
        case = e12_case_factory(
            registration__registration_date = registration_date,
            registration__investigations__mri_brain_requested_date = request_date,
        )

@patch.object(Investigations, "get_current_date", return_value=date(2023, 10, 1))
@pytest.mark.xfail    
@pytest.mark.django_db
def test_validation_request_or_performed_in_future(
    mocked_get_current_date,
    e12_case_factory,
):
    """Tests:
    - Neither Investigations.eeg_request_date nor Investigations.eeg_performed_date can be in the future
    - Neither Investigations.mri_brain_requested_date nor Investigations.mri_brain_reported_date can be in the future
    
    Patches today to always be 2023-10-1
    """
    
    # assign request date to 1 month after today
    request_date = date(2023, 10, 1) + relativedelta(months=1)
    # assign performed date to 2 months after today
    performed_date = date(2023,9,15) + relativedelta(months=2)
    
    print(Investigations.get_current_date())
    
    with pytest.raises(ValidationError):
        # try to save an investigation whose request date is after today
        case = e12_case_factory(
            registration__investigations__eeg_request_date = request_date,
        )
    with pytest.raises(ValidationError):
        # try to save an investigation whose request date is after today
        case = e12_case_factory(
            registration__investigations__mri_brain_requested_date = request_date,
        )
    with pytest.raises(ValidationError):
        # try to save an investigation whose performed date is after today
        case = e12_case_factory(
            registration__investigations__eeg_per_date = performed_date,
        )
    with pytest.raises(ValidationError):
        # try to save an investigation whose performed date is after today
        case = e12_case_factory(
            registration__investigations__mri_brain_reported_date = performed_date,
        )



@pytest.mark.xfail    
@pytest.mark.django_db
def test_validation_wait_calculation(
    e12_case_factory,
):
    """Tests:
    - Investigations.eeg_wait is only calculated if both Investigations.eeg_request_date and Investigations.eeg_performed_date are present and valid (including EEG declined date not set)
    - Investigations.mri_wait is only calculated if both Investigations.mri_brain_requested_date and Investigations.mri_brain_reported_date are present and valid (including MRI declined date not set)
    """
    
    # Save an investigation where eeg and mri were not requested + corresponding fields are None
    case = e12_case_factory(
        registration__investigations__eeg_not_requested = True,
        registration__investigations__mri_not_requested = True,
    )
    
    # Try calculating investigation wait
    with pytest.raises(ValidationError):
        case.registration.investigations.eeg_wait()
    with pytest.raises(ValidationError):
        case.registration.investigations.mri_wait()

