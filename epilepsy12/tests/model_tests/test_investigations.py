"""
Tests the Investigations model.

Tests:

    - 
"""

# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import (
    Investigations,
)

"""
- [ ] Investigations.eeg_request_date Investigations.eeg_performed_date should be None if Investigations.eeg_indicated is False or None
- [ ] Investigations.eeg_request_date cannot be after Investigations.eeg_performed_date
- [ ] Investigations.eeg_request_date cannot be before Registration.registration_date
- [ ] Neither Investigations.eeg_request_date nor Investigations.eeg_performed_date can be in the future
- [ ] Investigations.mri_brain_requested_date Investigations.mri_brain_reported_date should be None if Investigations.mri_indicated is False or None
- [ ] Investigations.mri_brain_requested_date cannot be after Investigations.mri_brain_reported_date
- [ ] Investigations.mri_brain_requested_date cannot be before Registration.registration_date
- [ ] Neither Investigations.mri_brain_requested_date nor Investigations.mri_brain_reported_date can be in the future
- [ ] Investigations.mri_wait is only calculated if both Investigations.mri_brain_requested_date and Investigations.mri_brain_reported_date are present and valid (including MRI declined date not set)
- [ ] Investigations.mri_wait is only calculated if both Investigations.eeg_request_date and Investigations.eeg_performed_date are present and valid (including EEG declined date not set)


"""


@pytest.mark.django_db
def test_registration_investigations_relation_success(
    e12Registration_2022,
):
    assert Investigations.objects.get(registration=e12Registration_2022)
