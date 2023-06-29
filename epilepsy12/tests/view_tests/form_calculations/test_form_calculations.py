"""
# Tests for `completed_fields` fn

These tests occur on a model-basis.

For each MODEL:

    1)
        - fill in ALL number of attributes
        - assert completed_fields(MODEL) == COUNT(ALL)
    2)
        - fill in random(X) number of attributes
        - assert completed_fields(MODEL) == X

- `Registration`

- `FirstPaediatricAssessment` 

    completed_fields(MODEL) == 6
        1. first_paediatric_assessment_in_acute_or_nonacute_setting
        2. has_number_of_episodes_since_the_first_been_documented
        3. general_examination_performed
        4. neurological_examination_performed
        5. developmental_learning_or_schooling_problems
        6. behavioural_or_emotional_problems

- `EpilepsyContext`

    completed_fields(MODEL) == 8
        1. previous_febrile_seizure
        2. previous_acute_symptomatic_seizure
        3. is_there_a_family_history_of_epilepsy
        4. previous_neonatal_seizures
        5. diagnosis_of_epilepsy_withdrawn
        6. were_any_of_the_epileptic_seizures_convulsive
        7. experienced_prolonged_generalized_convulsive_seizures
        8. experienced_prolonged_focal_seizures
    
- `Assessment`
- `Investigations`
- `Management`
    - `AntiepilepsyMedicine`
- `MultiaxialDiagnosis`
    - `Episode`
    - `Syndrome`
    

"""

# python imports
import pytest

# django imports
from django.urls import reverse

# E12 imports
# E12 imports
from epilepsy12.models import Epilepsy12User, Organisation, Case


@pytest.mark.skip(reason="Unfinished test.")
@pytest.mark.django_db
def test_completed_fields_success(
    client,
):
    """
    Simulating numerator in form calculation from numbers of scored fields in a given model is correct
    """
