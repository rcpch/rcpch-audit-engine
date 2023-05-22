"""
Tests the Multiaxial Diagnosis model

Test cases:
    - [ ] Ensure at least one MultiaxialDiagnosis.Episode.seizure_onset_date is after Registration.registration_date

"""
# Standard imports

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import (
    Episode,
)


@pytest.mark.django_db
def test_working_e12MultiaxialDiagnosis_e12Case_relation(
    e12MultiaxialDiagnosis_2022
):
    """Checks this multiaxialdiagnosis instance has a case attached
    """
    
    multiaxial_diagnosis = e12MultiaxialDiagnosis_2022
    
    assert multiaxial_diagnosis.registration.case
    
    
    

