""" Tests for `number_of_completed_fields_in_related_models` fn.

    MultiaxialDiagnosis - DONE
        - `Episode`
                for episode in Episodes:
                    EXPECTED_SCORE += 5 (if at least one episode is epileptic)
                    'seizure_onset_date'
                    'seizure_onset_date_confidence'
                    'episode_definition'
                    'has_description_of_the_episode_or_episodes_been_gathered'
                    'epilepsy_or_nonepilepsy_status'

                    if episode.has_description_of_the_episode_or_episodes_been_gathered:
                        EXPECTED_SCORE += 1
                        description
                    if episode.epilepsy_or_nonepilepsy_status == "E":
                        EXPECTED_SCORE += 1

                        if episode.epileptic_seizure_onset_type == "GO":
                            # 'generalised' onset: essential fields
                            # 'epileptic_generalised_onset'
                            EXPECTED_SCORE += 1
                        elif episode.epileptic_seizure_onset_type == "FO":
                            # focal onset
                            # minimum score is laterality
                            EXPECTED_SCORE += 1
                        else:
                            # either unclassified or unknown onset
                            # no further score
                            EXPECTED_SCORE += 0
                    elif episode.epilepsy_or_nonepilepsy_status == "NE":
                        # nonepileptic seizure - essential fields:
                        # nonepileptic_seizure_unknown_onset
                        # nonepileptic_seizure_type
                        # AND ONE of behavioural/migraine/misc/paroxysmal/sleep related/syncope - essential fields:
                        # nonepileptic_seizure_behavioural or
                        # nonepileptic_seizure_migraine or
                        # nonepileptic_seizure_miscellaneous or
                        # nonepileptic_seizure_paroxysmal or
                        # nonepileptic_seizure_sleep
                        # nonepileptic_seizure_syncope
                        
                        if episode.nonepileptic_seizure_type == "Oth":
                            EXPECTED_SCORE += 2
                        else:
                            EXPECTED_SCORE += 3
                    elif episode.epilepsy_or_nonepilepsy_status == "U":
                        # uncertain status
                        EXPECTED_SCORE += 0

    - `Syndrome`
        for syndrome in Syndromes:
            EXPECTED_SCORE += 2
            "syndrome_diagnosis_date"
            "syndrome__syndrome_name"

    - `Comorbidity`
        for comorbidity in Comorbidities:
            EXPECTED_SCORE += 2
            comorbidity_diagnosis_date"
            "comorbidity__comorbidityentity__conceptId"
Management
Registration
    
"""

# python imports
import pytest
from datetime import date
import random

# django imports

# E12 imports
from epilepsy12.models import (
    Syndrome,
    SyndromeList,
    Comorbidity,
    ComorbidityList,
    Site,
    Medicine,
)
from epilepsy12.common_view_functions.recalculate_form_generate_response import (
    number_of_completed_fields_in_related_models,
)
from epilepsy12.constants import (
    EPILEPSY_DIAGNOSIS_STATUS,
    EPILEPSY_SEIZURE_TYPE,
    GENERALISED_SEIZURE_TYPE,
    NON_EPILEPSY_SEIZURE_TYPE,
    NON_EPILEPSY_SEIZURE_ONSET,
    NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS,
    DATE_ACCURACY,
    EPISODE_DEFINITION,
    SEX_TYPE,
)


def get_random_answers_update_counter(answer_set: dict, counter: int):
    """Helper fn to return a random answer (None or valid value), and update counter of expected score.

    Args:
        answer_set (dict): current answer_set
        counter (int): current counter state

    Returns:
       answer_set (dict) : answer_set which can be provided to factory constructor
       counter (int): updated counter
    """

    for key, val in answer_set.items():
        answer = random.choice([None, val])
        answer_set[key] = answer

        # update counter
        if answer is not None:
            counter += 1

    return answer_set, counter


@pytest.mark.django_db
def test_related_model_fields_count_all_episode_fully_completed(
    e12_case_factory, e12_episode_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=multiaxialdiagnosis) returns correct counter when all Episode fields have an answer.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
    )
    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis
    return_value = number_of_completed_fields_in_related_models(multiaxial_diagnosis)
    assert (
        return_value == 0
    ), f"Empty episode, `number_of_completed_fields_in_related_models(multiaxial_diagnosis)` should return 0. Instead returned {return_value}"

    # Specific answer doesn't matter for these fields - just need an answer
    COMMON_FIELDS = {
        "seizure_onset_date": date(2023, 1, 1),
        "seizure_onset_date_confidence": DATE_ACCURACY[0][0],
        "episode_definition": EPISODE_DEFINITION[0][0],
        "has_description_of_the_episode_or_episodes_been_gathered": True,
        "description": "The seizure happened when child was watching TV",
    }

    EPILEPTIC_FOCAL_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[0][0],
        "focal_onset_left": True,
        "focal_onset_impaired_awareness": True,  # should not be counted!
    }
    EPILEPTIC_GENERALISED_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[1][0],
        "epileptic_generalised_onset": GENERALISED_SEIZURE_TYPE[0][0],
    }
    EPILEPTIC_UNKNOWN_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[2][0],
    }
    EPILEPTIC_UNCLASSIFIED_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[3][0],
    }
    NON_EPILEPTIC = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[1][0],
        "nonepileptic_seizure_type": NON_EPILEPSY_SEIZURE_TYPE[0][0],
        "nonepileptic_seizure_unknown_onset": NON_EPILEPSY_SEIZURE_ONSET[0][0],
        "nonepileptic_seizure_behavioural": NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS[0][
            0
        ],
    }
    UNCERTAIN = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[2][0],
    }

    # These are each answer sets which, combined with COMMON_FIELDS, will create a fully completed episode
    SEIZURE_TYPE_OPTIONS = [
        EPILEPTIC_FOCAL_ONSET,
        EPILEPTIC_GENERALISED_ONSET,
        EPILEPTIC_UNKNOWN_ONSET,
        EPILEPTIC_UNCLASSIFIED_ONSET,
        NON_EPILEPTIC,
        UNCERTAIN,
    ]

    # For each SEIZURE_TYPE_OPTION, create an Episode with COMMON_FIELDS and that SEIZURE_TYPE, make assertion
    factory_attributes = {**COMMON_FIELDS}
    for SEIZURE_TYPE in SEIZURE_TYPE_OPTIONS:
        episode = e12_episode_factory(
            multiaxial_diagnosis=multiaxial_diagnosis,
            **factory_attributes,
            **SEIZURE_TYPE,
        )

        return_value = number_of_completed_fields_in_related_models(
            multiaxial_diagnosis
        )

        expected_value = len(factory_attributes) + len(SEIZURE_TYPE)

        # DON'T COUNT OTHER RADIO BUTTONS FOR FOCAL ONSET
        if "focal_onset_impaired_awareness" in SEIZURE_TYPE:
            expected_value -= 1

        assert (
            return_value == expected_value
        ), f"Fully completed episodes run through `number_of_completed_fields_in_related_models(multiaxial_diagnosis)`. Expected {expected_value=} but received {return_value=}. Inserted Episode answer fields were: {factory_attributes}+{SEIZURE_TYPE}"

        # Reset for next seizure type
        episode.delete()


@pytest.mark.django_db
def test_related_model_fields_count_all_episode_random_answers(
    e12_case_factory, e12_episode_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=multiaxialdiagnosis) returns correct counter when Episode fields' answers are randomly either valid value or None.
    """

    counter = 0

    # Specific answer doesn't matter for these fields - just need an answer
    COMMON_FIELDS = {
        "seizure_onset_date": date(2023, 1, 1),
        "seizure_onset_date_confidence": DATE_ACCURACY[0][0],
        "episode_definition": EPISODE_DEFINITION[0][0],
        "has_description_of_the_episode_or_episodes_been_gathered": True,
        "description": "The seizure happened when child was watching TV",
    }

    EPILEPTIC_FOCAL_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[0][0],
        "focal_onset_left": True,
        "focal_onset_impaired_awareness": True,  # should not be counted!
    }
    EPILEPTIC_GENERALISED_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[1][0],
        "epileptic_generalised_onset": GENERALISED_SEIZURE_TYPE[0][0],
    }
    EPILEPTIC_UNKNOWN_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[2][0],
    }
    EPILEPTIC_UNCLASSIFIED_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[3][0],
    }
    NON_EPILEPTIC = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[1][0],
        "nonepileptic_seizure_type": NON_EPILEPSY_SEIZURE_TYPE[0][0],
        "nonepileptic_seizure_unknown_onset": NON_EPILEPSY_SEIZURE_ONSET[0][0],
        "nonepileptic_seizure_behavioural": NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS[0][
            0
        ],
    }
    UNCERTAIN = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[2][0],
    }

    SEIZURE_TYPE_OPTIONS = [
        EPILEPTIC_FOCAL_ONSET,
        EPILEPTIC_GENERALISED_ONSET,
        EPILEPTIC_UNKNOWN_ONSET,
        EPILEPTIC_UNCLASSIFIED_ONSET,
        NON_EPILEPTIC,
        UNCERTAIN,
    ]

    # Get random answer set for common fields
    COMMON_FIELDS, counter = get_random_answers_update_counter(
        answer_set=COMMON_FIELDS, counter=counter
    )

    # Create 5 randomly filled episodes, for each seizure type - ensures covers various different scenarios.
    for _ in range(5):
        for SEIZURE_TYPE in SEIZURE_TYPE_OPTIONS:
            SEIZURE_TYPE, expected_value = get_random_answers_update_counter(
                answer_set=SEIZURE_TYPE, counter=counter
            )

            # DON'T COUNT OTHER RADIO BUTTONS FOR FOCAL ONSET, regardless of answer
            if SEIZURE_TYPE.get("focal_onset_impaired_awareness") is not None:
                expected_value -= 1

            factory_attributes = {**COMMON_FIELDS, **SEIZURE_TYPE}

            # Need a case to make an episode
            CASE = e12_case_factory(
                first_name=f"temp_child_{GOSH.name}",
                organisations__organisation=GOSH,
            )
            multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

            episode = e12_episode_factory(
                multiaxial_diagnosis=multiaxial_diagnosis,
                **factory_attributes,
            )

            return_value = number_of_completed_fields_in_related_models(
                multiaxial_diagnosis
            )

            assert (
                return_value == expected_value
            ), f"Randomly completed episodes run through `number_of_completed_fields_in_related_models(multiaxial_diagnosis)`. Expected {expected_value=} but received {return_value=}. Inserted Episode answer fields: {factory_attributes}+{SEIZURE_TYPE}"

            # Reset for next seizure type
            episode.delete()


@pytest.mark.django_db
def test_related_model_fields_count_all_syndrome_fully_completed(
    e12_case_factory, e12_syndrome_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=multiaxialdiagnosis) returns correct counter when all syndrome fields have an answer.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
    )
    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis
    return_value = number_of_completed_fields_in_related_models(multiaxial_diagnosis)
    assert (
        return_value == 0
    ), f"Empty syndrome, `number_of_completed_fields_in_related_models(multiaxial_diagnosis)` should return 0. Instead returned {return_value}"

    factory_attributes = {
        "syndrome_diagnosis_date": date(2023, 1, 1),
        "syndrome": SyndromeList.objects.get(syndrome_name="Rasmussen syndrome"),
    }

    syndrome = e12_syndrome_factory(
        multiaxial_diagnosis=multiaxial_diagnosis, **factory_attributes
    )

    return_value = number_of_completed_fields_in_related_models(multiaxial_diagnosis)

    expected_value = len(factory_attributes)

    assert (
        return_value == expected_value
    ), f"Fully completed Syndrome run through `number_of_completed_fields_in_related_models(multiaxial_diagnosis)`. Expected {expected_value=} but received {return_value=}. Inserted answer fields were: {factory_attributes}"


@pytest.mark.django_db
def test_related_model_fields_count_all_syndrome_random_answers(
    e12_case_factory, e12_syndrome_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=multiaxialdiagnosis) returns correct counter when syndrome fields' answers are randomly either valid value or None.
    """

    counter = 0

    factory_attributes_list = []
    SYNDROME_NAMES = SyndromeList.objects.all()[:5]
    # Create 5 randomly filled syndromes - ensures covers various different scenarios.
    for i in range(5):
        inital_answer = {
            "syndrome_diagnosis_date": date(2023, 1, 1),
            "syndrome": SYNDROME_NAMES[i],
        }
        # Get random answer set for fields
        ANSWER_SET, expected_value = get_random_answers_update_counter(
            answer_set=inital_answer, counter=counter
        )
        factory_attributes_list.append((ANSWER_SET, expected_value))

    for factory_attributes, expected_value in factory_attributes_list:
        # Need a case to make an syndrome
        CASE = e12_case_factory(
            first_name=f"temp_child_{GOSH.name}",
            organisations__organisation=GOSH,
        )
        multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

        syndrome = e12_syndrome_factory(
            multiaxial_diagnosis=multiaxial_diagnosis,
            **factory_attributes,
        )

        return_value = number_of_completed_fields_in_related_models(
            multiaxial_diagnosis
        )

        assert (
            return_value == expected_value
        ), f"Randomly completed syndromes run through `number_of_completed_fields_in_related_models(multiaxial_diagnosis)`. Expected {expected_value=} but received {return_value=}. Inserted answer fields: {factory_attributes}"

        # Reset for next seizure type
        syndrome.delete()


@pytest.mark.django_db
def test_related_model_fields_count_all_comorbidity_fully_completed(
    e12_case_factory, e12_comorbidity_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=multiaxialdiagnosis) returns correct counter when all comorbidity fields have an answer.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
    )
    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis
    return_value = number_of_completed_fields_in_related_models(multiaxial_diagnosis)
    assert (
        return_value == 0
    ), f"Empty comorbidity, `number_of_completed_fields_in_related_models(multiaxial_diagnosis)` should return 0. Instead returned {return_value}"

    factory_attributes = {
        "comorbidity_diagnosis_date": date(2023, 1, 1),
        "comorbidityentity": ComorbidityList.objects.first(),
    }

    comorbidity = e12_comorbidity_factory(
        multiaxial_diagnosis=multiaxial_diagnosis, **factory_attributes
    )

    return_value = number_of_completed_fields_in_related_models(multiaxial_diagnosis)

    expected_value = len(factory_attributes)

    assert (
        return_value == expected_value
    ), f"Fully completed comorbidity run through `number_of_completed_fields_in_related_models(multiaxial_diagnosis)`. Expected {expected_value=} but received {return_value=}. Inserted answer fields were: {factory_attributes}"


@pytest.mark.django_db
def test_related_model_fields_count_all_comorbidity_random_answers(
    e12_case_factory, e12_comorbidity_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=multiaxialdiagnosis) returns correct counter when comorbidity fields' answers are randomly either valid value or None.
    """

    counter = 0

    factory_attributes_list = []
    COMORBIDITY_NAMES = ComorbidityList.objects.all()[:5]
    # Create 5 randomly filled comorbiditys - ensures covers various different scenarios.
    for i in range(len(COMORBIDITY_NAMES)):
        # Comorbidity.comorbidityentity CANNOT be None, so only have diagnosis date's random answer options include None
        inital_answer = {
            "comorbidity_diagnosis_date": date(2023, 1, 1),
        }
        # Get random answer set for fields
        ANSWER_SET, expected_value = get_random_answers_update_counter(
            answer_set=inital_answer, counter=counter
        )
        ANSWER_SET.update({"comorbidityentity": COMORBIDITY_NAMES[i]})
        expected_value += 1

        factory_attributes_list.append((ANSWER_SET, expected_value))

    for factory_attributes, expected_value in factory_attributes_list:
        # Need a case to make an comorbidity
        CASE = e12_case_factory(
            first_name=f"temp_child_{GOSH.name}",
            organisations__organisation=GOSH,
        )
        multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

        comorbidity = e12_comorbidity_factory(
            multiaxial_diagnosis=multiaxial_diagnosis,
            **factory_attributes,
        )

        return_value = number_of_completed_fields_in_related_models(
            multiaxial_diagnosis
        )

        assert (
            return_value
            == expected_value  # Have to add 1 as comorbidityentity is always set, but outside the helper fn to updated expected_value
        ), f"Randomly completed comorbiditys run through `number_of_completed_fields_in_related_models(multiaxial_diagnosis)`. Expected {expected_value=} but received {return_value=}. Inserted answer fields: {factory_attributes}"

        # Reset for next seizure type
        comorbidity.delete()


@pytest.mark.django_db
def test_related_model_fields_count_assessment(e12_case_factory, GOSH):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=assessment) returns correct counter when Site fields' answers are filled.
    """
    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
    )
    assessment = CASE.registration.assessment
    return_value = number_of_completed_fields_in_related_models(assessment)
    assert (
        return_value == 0
    ), f"Empty assessment with relevant Site vars False, `number_of_completed_fields_in_related_models(assessment)` should return 0. Instead returned {return_value}"

    site = Site.objects.get(case=CASE)
    site.site_is_childrens_epilepsy_surgery_centre = True
    site.site_is_general_paediatric_centre = True
    site.site_is_paediatric_neurology_centre = True
    site.save()

    return_value = number_of_completed_fields_in_related_models(assessment)
    expected_value = 3

    assert (
        return_value == expected_value
    ), f"Site values all True for `number_of_completed_fields_in_related_models(assessment)`. Expected {expected_value=} but received {return_value=}"


@pytest.mark.django_db
def test_related_model_fields_count_management(
    e12_case_factory, e12_anti_epilepsy_medicine_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=management) returns correct counter when AED fields' answers are filled.
    """
    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        sex=SEX_TYPE[2][0],
    )
    management = CASE.registration.management
    return_value = number_of_completed_fields_in_related_models(management)
    assert (
        return_value == 0
    ), f"Empty management, `number_of_completed_fields_in_related_models(management)` should return 0. Instead returned {return_value}"

    management.has_an_aed_been_given = True
    management.has_rescue_medication_been_prescribed = True
    management.save()

    aed_answers = {
        "medicine_entity": Medicine.objects.get(medicine_name="Sodium valproate"),
        "antiepilepsy_medicine_start_date": date(2023, 1, 1),
        "antiepilepsy_medicine_risk_discussed": True,
        "is_a_pregnancy_prevention_programme_in_place": True,
        "has_a_valproate_annual_risk_acknowledgement_form_been_completed": True,
    }
    aed = e12_anti_epilepsy_medicine_factory(
        management=management,
        is_rescue_medicine=False,
        **aed_answers,
    )
    rescue_medicine_answers = {
        "medicine_entity": Medicine.objects.get(medicine_name="Levetiracetam"),
        "antiepilepsy_medicine_start_date": date(2023, 1, 1),
        "antiepilepsy_medicine_risk_discussed": True,
    }
    rescue_medicine = e12_anti_epilepsy_medicine_factory(
        management=management,
        is_rescue_medicine=True,
        **rescue_medicine_answers,
    )
    return_value = number_of_completed_fields_in_related_models(management)

    expected_value = len(rescue_medicine_answers) + len(aed_answers)

    assert (
        return_value == expected_value
    ), f"AED values all filled and valid for `number_of_completed_fields_in_related_models(management)`. Expected {expected_value=} but received {return_value=}"


@pytest.mark.django_db
def test_related_model_fields_count_registration(e12_case_factory, GOSH):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=registration) returns correct counter when Site fields' answers are filled.

    NOTE: expected_value == 1 as default factory has:
        - site_is_primary_centre_of_epilepsy_care=True
        - site_is_actively_involved_in_epilepsy_care=True
    """
    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
    )

    return_value = number_of_completed_fields_in_related_models(CASE.registration)

    expected_value = 1

    assert (
        return_value == expected_value
    ), f"Site values all True for `number_of_completed_fields_in_related_models(registration)`. Expected {expected_value=} but received {return_value=}"
