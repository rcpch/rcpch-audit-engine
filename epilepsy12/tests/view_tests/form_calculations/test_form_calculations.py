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

    EXPECTED_SCORE=completed_fields(MODEL) == 5
        1. "childrens_epilepsy_surgical_service_referral_criteria_met"
        2. "consultant_paediatrician_referral_made"
        3. "paediatric_neurologist_referral_made"
        4. "childrens_epilepsy_surgical_service_referral_made"
        5. "epilepsy_specialist_nurse_referral_made"

        if "consultant_paediatrician_referral_made" == True
            EXPECTED_SCORE+=3
            'general_paediatric_centre'
            'consultant_paediatrician_referral_date'
            'consultant_paediatrician_input_date'
            
            number_of_completed_fields_in_related_models = 1
            general_paediatric_centre
        
        if "paediatric_neurologist_referral_made" == True
            EXPECTED_SCORE+=3
            'paediatric_neurology_centre'
            'paediatric_neurologist_referral_date'
            'paediatric_neurologist_input_date'
            
            number_of_completed_fields_in_related_models = 1
            'paediatric_neurology_centre'
        
        if "childrens_epilepsy_surgical_service_referral_made" == True
            EXPECTED_SCORE+=3
            'epilepsy_surgery_centre'
            'childrens_epilepsy_surgical_service_referral_date'
            'childrens_epilepsy_surgical_service_input_date'
            
            number_of_completed_fields_in_related_models = 1
            'epilepsy_surgery_centre'
        
        if "epilepsy_specialist_nurse_referral_made" == True
            EXPECTED_SCORE+=2
            'epilepsy_specialist_nurse_referral_date'
            'epilepsy_specialist_nurse_input_date'
            

- `Investigations`
    
    EXPECTED_SCORE=completed_fields(MODEL) == 4
    'eeg_indicated'
    'twelve_lead_ecg_status'
    'ct_head_scan_status'
    'mri_indicated'

    if 'eeg_indicated' == True:
        EXPECTED_SCORE+=2
        'eeg_request_date'
        'eeg_performed_date'
    if mri_indicated == True:
        EXPECTED_SCORE+=2
        'mri_brain_requested_date'
        'mri_brain_reported_date'

- `Management`
    EXPECTED_SCORE = 5
    'has_an_aed_been_given'
    'has_rescue_medication_been_prescribed'
    'individualised_care_plan_in_place'
    'has_been_referred_for_mental_health_support'
    'has_support_for_mental_health_support'

    if 'has_rescue_medication_been_prescribed' == True
        for medicine in AntiepilepsyMedicine.all(is_rescue_medicine=True)
            number_of_completed_fields_in_related_models += 3
            is_rescue_medicine
            antiepilepsy_medicine_start_date
            antiepilepsy_medicine_risk_discussed

    if 'has_an_aed_been_given' == True
        for medicine in AntiepilepsyMedicine.all(is_rescue_medicine=False)
            number_of_completed_fields_in_related_models += 3
            is_rescue_medicine
            antiepilepsy_medicine_start_date
            antiepilepsy_medicine_risk_discussed
            
            if case.sex == 2 and age >= 12 and is_a_pregnancy_prevention_programme_needed==True:
                number_of_completed_fields_in_related_models += 2
                has_a_valproate_annual_risk_acknowledgement_form_been_completed
                is_a_pregnancy_prevention_programme_in_place


    if 'individualised_care_plan_in_place' == True
        EXPECTED_SCORE += 10
        'individualised_care_plan_date'
        'individualised_care_plan_has_parent_carer_child_agreement'
        'individualised_care_plan_includes_service_contact_details'
        'individualised_care_plan_include_first_aid'
        'individualised_care_plan_parental_prolonged_seizure_care'
        'individualised_care_plan_includes_general_participation_risk'
        'individualised_care_plan_addresses_water_safety'
        'individualised_care_plan_addresses_sudep'
        'individualised_care_plan_includes_ehcp'
        'has_individualised_care_plan_been_updated_in_the_last_year'


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
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    Case,
    Registration,
    FirstPaediatricAssessment,
)
from epilepsy12.common_view_functions import completed_fields
from epilepsy12.constants import (
    CHRONICITY,
)


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

    assert (
        completed_fields(registration) == 0
    ), f"Empty registration, `completed_fields(registration)` should return 0. Instead returned {completed_fields(registration)}"

    registration.registration_date = date(2023, 1, 1)
    registration.eligibility_criteria_met = True
    registration.save()

    assert (
        completed_fields(registration) == 2
    ), f"Completed registration, `completed_fields(registration)` should return 2. . Instead returned {completed_fields(registration)}"


@pytest.mark.django_db
def test_completed_fields_registration_random_fields(e12_case_factory, GOSH):
    """
    Simulating completed_fields(model_instance=Registration) returns correct counter when fields randomly have an answer or left None.
    """
    EXPECTED_SCORE = 0

    REGISTRATION_DATE = random.choice([None, date(2023, 1, 1)])
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

    assert (
        completed_fields(registration) == EXPECTED_SCORE
    ), f"Randomly completed registration, `completed_fields(registration)` should return {EXPECTED_SCORE}. Instead returned {completed_fields(registration)}"


@pytest.mark.django_db
def test_completed_fields_first_paediatric_assessment_all_fields(
    e12_case_factory, GOSH
):
    """
    Simulating completed_fields(model_instance=first_paediatric_assessment) returns correct counter when all fields have an answer.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
    )

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        registration=CASE.registration
    )

    assert (
        completed_fields(first_paediatric_assessment) == 0
    ), f"Empty first_paediatric_assessment, `completed_fields(first_paediatric_assessment)` should return 0. Instead returned {completed_fields(first_paediatric_assessment)}"

    fields_and_answers = {
        "first_paediatric_assessment_in_acute_or_nonacute_setting": CHRONICITY[0][0],
        "has_number_of_episodes_since_the_first_been_documented": True,
        "general_examination_performed": True,
        "neurological_examination_performed": True,
        "developmental_learning_or_schooling_problems": True,
        "behavioural_or_emotional_problems": True,
    }
    factory_attributes = {
        f"registration__first_paediatric_assessment__{field}": answer
        for field, answer in fields_and_answers.items()
    }

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        **factory_attributes,
    )

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        registration=CASE.registration
    )

    assert completed_fields(first_paediatric_assessment) == len(
        fields_and_answers
    ), f"Completed first_paediatric_assessment, `completed_fields(first_paediatric_assessment)` should return {len(fields_and_answers)}. Instead returned {completed_fields(first_paediatric_assessment)}"


@pytest.mark.django_db
def test_completed_fields_first_paediatric_assessment_random_fields(
    e12_case_factory, GOSH
):
    """
    Simulating completed_fields(model_instance=first_paediatric_assessment) returns correct counter when random fields have an answer or None.
    """

    fields_and_answers = {
        "first_paediatric_assessment_in_acute_or_nonacute_setting": random.choice(
            [None, CHRONICITY[0][0]]
        ),
        "has_number_of_episodes_since_the_first_been_documented": random.choice(
            [None, True]
        ),
        "general_examination_performed": random.choice([None, True]),
        "neurological_examination_performed": random.choice([None, True]),
        "developmental_learning_or_schooling_problems": random.choice([None, True]),
        "behavioural_or_emotional_problems": random.choice([None, True]),
    }
    EXPECTED_SCORE = 0
    for answer in fields_and_answers.values():
        if answer is not None:
            EXPECTED_SCORE += 1

    factory_attributes = {
        f"registration__first_paediatric_assessment__{field}": answer
        for field, answer in fields_and_answers.items()
    }

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        **factory_attributes,
    )

    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
        registration=CASE.registration
    )

    assert (
        completed_fields(first_paediatric_assessment) == EXPECTED_SCORE
    ), f"Randomly completed first_paediatric_assessment, `completed_fields(first_paediatric_assessment)` should return {EXPECTED_SCORE}. Instead returned {completed_fields(first_paediatric_assessment)}. Answers: {fields_and_answers}"
