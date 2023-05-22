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
    MultiaxialDiagnosis,
    Episode,
)


@pytest.mark.django_db
def test_working_e12MultiaxialDiagnosis_e12Case_relation(
    e12Registration_2022
):
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(registration=e12Registration_2022)
    
    print(multiaxial_diagnosis.registration)
    
    episode = Episode.objects.get(multiaxial_diagnosis=multiaxial_diagnosis)

    print(f"{episode.seizure_onset_date}")
    
    

