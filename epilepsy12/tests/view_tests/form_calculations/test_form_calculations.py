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
from datetime import date
import random

# django imports
from django.urls import reverse

# E12 imports
from epilepsy12.models import Epilepsy12User, Organisation, Case, Registration
from epilepsy12.common_view_functions import completed_fields


@pytest.mark.django_db
def test_completed_fields_registration_all_fields(e12_case_factory, GOSH):
    """
    Simulating completed_fields(model_instance=Registration) returns correct counter when all fields have an answer.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__registration_date=None,
        registration__eligibility_criteria_met=None,
    )

    registration = Registration.objects.get(case=CASE)

    assert completed_fields(registration) == 0, f"Empty registration, `completed_fields(registration)` should return 0. Instead returned {completed_fields(registration)}"

    registration.registration_date = date(2023, 1, 1)
    registration.eligibility_criteria_met = True
    registration.save()

    assert completed_fields(registration) == 2, f"Completed registration, `completed_fields(registration)` should return 2. . Instead returned {completed_fields(registration)}"

@pytest.mark.django_db
def test_completed_fields_registration_random_fields(e12_case_factory, GOSH):
    """
    Simulating completed_fields(model_instance=Registration) returns correct counter when fields randomly have an answer or left None.
    """
    EXPECTED_SCORE = 0
    
    REGISTRATION_DATE = random.choice([None,date(2023,1,1)])
    if REGISTRATION_DATE is not None:
        EXPECTED_SCORE += 1
    
    ELIGIBILITY_CRITERIA_MET = random.choice([None, True])
    if ELIGIBILITY_CRITERIA_MET is not None:
        EXPECTED_SCORE += 1

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__registration_date=REGISTRATION_DATE,
        registration__eligibility_criteria_met=ELIGIBILITY_CRITERIA_MET,
    )

    registration = Registration.objects.get(case=CASE)

    assert completed_fields(registration) == EXPECTED_SCORE, f"Randomly completed registration, `completed_fields(registration)` should return {EXPECTED_SCORE}. Instead returned {completed_fields(registration)}"