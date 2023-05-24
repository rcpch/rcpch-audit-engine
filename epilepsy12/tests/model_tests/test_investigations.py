"""
Tests the Investigations model.

Tests:
- [ ] Investigations.eeg_request_date # TODO what should go here?
= [x] Investigations.eeg_performed_date should be None if Investigations.eeg_indicated is False or None
- [ ] Investigations.eeg_request_date cannot be after Investigations.eeg_performed_date
- [ ] Investigations.eeg_request_date cannot be before Registration.registration_date
- [ ] Neither Investigations.eeg_request_date nor Investigations.eeg_performed_date can be in the future
- [x] Investigations.mri_brain_requested_date Investigations.mri_brain_reported_date should be None if Investigations.mri_indicated is False or None
- [ ] Investigations.mri_brain_requested_date cannot be after Investigations.mri_brain_reported_date
- [ ] Investigations.mri_brain_requested_date cannot be before Registration.registration_date
- [ ] Neither Investigations.mri_brain_requested_date nor Investigations.mri_brain_reported_date can be in the future
- [ ] Investigations.mri_wait is only calculated if both Investigations.mri_brain_requested_date and Investigations.mri_brain_reported_date are present and valid (including MRI declined date not set)
- [ ] Investigations.mri_wait is only calculated if both Investigations.eeg_request_date and Investigations.eeg_performed_date are present and valid (including EEG declined date not set)

"""

# Standard imports
from datetime import date

# Third party imports
import pytest
from django.core.exceptions import ValidationError

# RCPCH imports


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
        # Create an Investigations object where mri_brain_indicated = False, and related fields None, then .mri_brain_performed_date to a date, attempts to save it.
        e12_case_factory(
            registration__investigations__mri_brain_not_requested = True,
            registration__investigations__mri_brain_performed_date = performed_date
        )
    
    
        
