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

- `Registration` - DONE

- `FirstPaediatricAssessment` - DONE

    completed_fields(MODEL) == 6
        1. first_paediatric_assessment_in_acute_or_nonacute_setting
        2. has_number_of_episodes_since_the_first_been_documented
        3. general_examination_performed
        4. neurological_examination_performed
        5. developmental_learning_or_schooling_problems
        6. behavioural_or_emotional_problems

- `EpilepsyContext` - DONE

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
    EpilepsyContext,
    Assessment,
)
from epilepsy12.common_view_functions import completed_fields
from epilepsy12.constants import (
    CHRONICITY,
    OPT_OUT_UNCERTAIN,
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


@pytest.mark.django_db
def test_completed_fields_epilepsy_context_all_fields(e12_case_factory, GOSH):
    """
    Simulating completed_fields(model_instance=epilepsy_context) returns correct counter when all fields have an answer.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
    )

    epilepsy_context = FirstPaediatricAssessment.objects.get(
        registration=CASE.registration
    )

    assert (
        completed_fields(epilepsy_context) == 0
    ), f"Empty epilepsy_context, `completed_fields(epilepsy_context)` should return 0. Instead returned {completed_fields(epilepsy_context)}"

    fields_and_answers = {
        "previous_febrile_seizure": OPT_OUT_UNCERTAIN[0][0],
        "previous_acute_symptomatic_seizure": OPT_OUT_UNCERTAIN[0][0],
        "is_there_a_family_history_of_epilepsy": OPT_OUT_UNCERTAIN[0][0],
        "previous_neonatal_seizures": OPT_OUT_UNCERTAIN[0][0],
        "diagnosis_of_epilepsy_withdrawn": True,
        "were_any_of_the_epileptic_seizures_convulsive": True,
        "experienced_prolonged_generalized_convulsive_seizures": OPT_OUT_UNCERTAIN[0][
            0
        ],
        "experienced_prolonged_focal_seizures": OPT_OUT_UNCERTAIN[0][0],
    }
    factory_attributes = {
        f"registration__epilepsy_context__{field}": answer
        for field, answer in fields_and_answers.items()
    }

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        **factory_attributes,
    )

    epilepsy_context = EpilepsyContext.objects.get(registration=CASE.registration)

    assert completed_fields(epilepsy_context) == len(
        fields_and_answers
    ), f"Completed epilepsy_context, `completed_fields(epilepsy_context)` should return {len(fields_and_answers)}. Instead returned {completed_fields(epilepsy_context)}"


@pytest.mark.django_db
def test_completed_fields_epilepsy_context_random_fields(e12_case_factory, GOSH):
    """
    Simulating completed_fields(model_instance=epilepsy_context) returns correct counter when random fields have an answer.
    """

    CHAR_CHOICE_FIELDS = [
        "previous_febrile_seizure",
        "previous_acute_symptomatic_seizure",
        "is_there_a_family_history_of_epilepsy",
        "previous_neonatal_seizures",
        "experienced_prolonged_generalized_convulsive_seizures",
        "experienced_prolonged_focal_seizures",
    ]
    BOOL_FIELDS = [
        "diagnosis_of_epilepsy_withdrawn",
        "were_any_of_the_epileptic_seizures_convulsive",
    ]

    factory_attributes = {}
    EXPECTED_SCORE = 0

    for field in CHAR_CHOICE_FIELDS:
        BASE_KEY_NAME = f"registration__epilepsy_context__{field}"

        answer = random.choice([None, OPT_OUT_UNCERTAIN])
        if answer is not None:
            answer = answer[0][0]
            EXPECTED_SCORE += 1

        factory_attributes.update({BASE_KEY_NAME: answer})

    for field in BOOL_FIELDS:
        BASE_KEY_NAME = f"registration__epilepsy_context__{field}"

        answer = random.choice([None, True])
        if answer is not None:
            EXPECTED_SCORE += 1

        factory_attributes.update({BASE_KEY_NAME: answer})

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        **factory_attributes,
    )

    epilepsy_context = EpilepsyContext.objects.get(registration=CASE.registration)

    assert (
        completed_fields(epilepsy_context) == EXPECTED_SCORE
    ), f"Randomly completed epilepsy_context, `completed_fields(epilepsy_context)` should return {EXPECTED_SCORE}. Instead returned {completed_fields(epilepsy_context)}. Answers: {factory_attributes}"


@pytest.mark.django_db
def test_completed_fields_assessment_all_fields(e12_case_factory, GOSH):
    """
    Simulating completed_fields(model_instance=assessment) returns correct counter when all fields have an answer.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
    )

    assessment = Assessment.objects.get(registration=CASE.registration)

    assert (
        completed_fields(assessment) == 0
    ), f"Empty assessment, `completed_fields(assessment)` should return 0. Instead returned {completed_fields(assessment)}"

    fields_and_answers = {
        "childrens_epilepsy_surgical_service_referral_criteria_met": True,
        "consultant_paediatrician_referral_made": True,
        "consultant_paediatrician_referral_date": date(2023, 1, 1),
        "consultant_paediatrician_input_date": date(2023, 1, 2),
        "paediatric_neurologist_referral_made": True,
        "paediatric_neurologist_referral_date": date(2023, 1, 1),
        "paediatric_neurologist_input_date": date(2023, 1, 2),
        "childrens_epilepsy_surgical_service_referral_made": True,
        "childrens_epilepsy_surgical_service_referral_date": date(2023, 1, 1),
        "childrens_epilepsy_surgical_service_input_date": date(2023, 1, 2),
        "epilepsy_specialist_nurse_referral_made": True,
        "epilepsy_specialist_nurse_referral_date": date(2023, 1, 1),
        "epilepsy_specialist_nurse_input_date": date(2023, 1, 2),
    }

    factory_attributes = {
        f"registration__assessment__{field}": answer
        for field, answer in fields_and_answers.items()
    }

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        **factory_attributes,
    )

    assessment = Assessment.objects.get(registration=CASE.registration)

    assert completed_fields(assessment) == len(
        fields_and_answers
    ), f"Completed assessment, `completed_fields(assessment)` should return {len(fields_and_answers)}. Instead returned {completed_fields(assessment)}"


@pytest.mark.django_db
def test_completed_fields_assessment_random_fields(e12_case_factory, GOSH):
    """
    Simulating completed_fields(model_instance=assessment) returns correct counter when random fields have an answer.
    """

    factory_attributes = {}
    EXPECTED_SCORE = 0
    BASE_KEY_NAME = "registration__assessment__"

    # This field has no dependent date fields
    KEY_NAME = (
        BASE_KEY_NAME + "childrens_epilepsy_surgical_service_referral_criteria_met"
    )

    ANSWER = random.choice([None, True])
    factory_attributes.update({KEY_NAME: ANSWER})
    if ANSWER is not None:
        EXPECTED_SCORE += 1

    # All other bool fields have dependent date fields
    BOOL_FIELDS = [
        "consultant_paediatrician",
        "paediatric_neurologist",
        "childrens_epilepsy_surgical_service",
        "epilepsy_specialist_nurse",
    ]
    DATE_1 = date(2023, 1, 1)
    DATE_2 = date(2023, 1, 2)

    for bool_field in BOOL_FIELDS:
        factory_attributes.update({KEY_NAME: ANSWER})

        KEY_NAME = BASE_KEY_NAME + f"{bool_field}_referral_made"
        ANSWER = random.choice([None, True])

        DATE_1_ANSWER_OPTIONS = [None]
        DATE_2_ANSWER_OPTIONS = [None]

        if ANSWER is not None:
            # Opens up 2 date options
            EXPECTED_SCORE += 1
            DATE_1_ANSWER_OPTIONS += [DATE_1]
            DATE_2_ANSWER_OPTIONS += [DATE_2]

        REFERRAL_KEY_NAME = BASE_KEY_NAME + f"{bool_field}_referral_date"
        REFERRAL_ANSWER = random.choice(DATE_1_ANSWER_OPTIONS)
        if REFERRAL_ANSWER is not None:
            EXPECTED_SCORE += 1

        INPUT_KEY_NAME = BASE_KEY_NAME + f"{bool_field}_input_date"
        INPUT_ANSWER = random.choice(DATE_2_ANSWER_OPTIONS)
        if INPUT_ANSWER is not None:
            EXPECTED_SCORE += 1

        date_answers = {
            REFERRAL_KEY_NAME: REFERRAL_ANSWER,
            INPUT_KEY_NAME: INPUT_ANSWER,
        }
        factory_attributes.update(date_answers)

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        **factory_attributes,
    )

    assessment = Assessment.objects.get(registration=CASE.registration)

    assert (
        completed_fields(assessment) == EXPECTED_SCORE
    ), f"Randomly completed assessment, `completed_fields(assessment)` should return {EXPECTED_SCORE}. Instead returned {completed_fields(assessment)}. Answers: {factory_attributes}"
