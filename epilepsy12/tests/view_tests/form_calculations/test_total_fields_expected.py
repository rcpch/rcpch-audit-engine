""" Tests for `total_fields_expected` fn and `scoreable_fields_for_model_class_name` helper fn.

All models EXCEPT the following 5 simply return the output of `scoreable_fields_for_model_class_name`. 

Additionally, these 5 use `scoreable_fields_for_model_class_name` += some extra fields in related models.

    1. MultiaxialDiagnosis
    2. Assessment
    3. Investigations
    4. Management
    5. Registration
"""

# Python imports
import pytest
from datetime import date
from dateutil.relativedelta import relativedelta
import random

# Django imports

# E12 imports
from epilepsy12.models import (
    Episode,
    SyndromeEntity,
    MedicineEntity,
)
from epilepsy12.common_view_functions.recalculate_form_generate_response import (
    scoreable_fields_for_model_class_name,
    total_fields_expected,
    count_episode_fields,
)
from epilepsy12.constants import (
    Registration_minimum_scorable_fields,
    EpilepsyContext_minimum_scorable_fields,
    FirstPaediatricAssessment_minimum_scorable_fields,
    MultiaxialDiagnosis_minimum_scorable_fields,
    Episode_minimum_scorable_fields,
    Syndrome_minimum_scorable_fields,
    Comorbidity_minimum_scorable_fields,
    Assessment_minimum_scorable_fields,
    Investigations_minimum_scorable_fields,
    Management_minimum_scorable_fields,
    AntiEpilepsyMedicine_minimum_scorable_fields,
    SEX_TYPE,
    EPILEPSY_DIAGNOSIS_STATUS,
    NON_EPILEPSY_SEIZURE_ONSET,
    NON_EPILEPSY_SEIZURE_TYPE,
)
from epilepsy12.tests.view_tests.form_calculations.test_number_of_completed_fields_in_related_models import (
    get_random_answers_update_counter,
)


def test_correct_output_scoreable_fields_for_model_class_name():
    """
    Tests the scoreable_fields_for_model_class_name function returns correct score for all models.
    """

    model_expected_fields = [
        Registration_minimum_scorable_fields,
        EpilepsyContext_minimum_scorable_fields,
        FirstPaediatricAssessment_minimum_scorable_fields,
        MultiaxialDiagnosis_minimum_scorable_fields,
        Episode_minimum_scorable_fields,
        Syndrome_minimum_scorable_fields,
        Comorbidity_minimum_scorable_fields,
        Assessment_minimum_scorable_fields,
        Investigations_minimum_scorable_fields,
        Management_minimum_scorable_fields,
        AntiEpilepsyMedicine_minimum_scorable_fields,
    ]

    for model in model_expected_fields:
        return_value = scoreable_fields_for_model_class_name(model.model_name)

        expected_value = len(model.all_fields)

        assert (
            return_value == expected_value
        ), f"scoreable_fields_for_model_class_name({model.model_name}) should return {expected_value}, instead returned {return_value}."


@pytest.mark.django_db
def test_count_episode_fields_epileptic_focal_onset(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single Episode queryset returns correct expected output, with a completed episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_focal_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value == 8
    ), f"Single completely filled Focal Onset Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return 8. Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_epileptic_generalised_onset(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single Episode queryset returns correct expected output, with a completed episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_generalised_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value == 8
    ), f"Single completely filled Generalised Onset Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return 8. Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_epileptic_unclassified_onset(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single Episode queryset returns correct expected output, with a completed episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_unclassified_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value == 7
    ), f"Single completely filled unclassified Onset Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return 7. Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_epileptic_unknown_onset(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single Episode queryset returns correct expected output, with a completed episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_unknown_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value == 7
    ), f"Single completely filled unknown Onset Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return 7. Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_nonepileptic(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single non epileptic Episode queryset returns correct expected output, with a completed episode.
    """
    expected_value = 11  # 5 for incomplete epileptic episode, ++6 for non epileptic episode base value incomplete fields

    # Either BPP (++3 to expected score) OR Oth (++2 to expected score)
    seizure_type_answer = random.choice(
        [NON_EPILEPSY_SEIZURE_TYPE[0][0], NON_EPILEPSY_SEIZURE_TYPE[-1][0]]
    )

    if seizure_type_answer == NON_EPILEPSY_SEIZURE_TYPE[0][0]:
        expected_value += 3
    else:
        expected_value += 2
    answer_set = {
        "registration__multiaxial_diagnosis__episode__epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[
            1
        ][
            0
        ],
        "registration__multiaxial_diagnosis__episode__nonepileptic_seizure_unknown_onset": NON_EPILEPSY_SEIZURE_ONSET[
            0
        ][
            0
        ],
        "registration__multiaxial_diagnosis__episode__nonepileptic_seizure_type": seizure_type_answer,
    }

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__common_fields=True,
        **answer_set,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value == expected_value
    ), f"Single completely filled non epileptic Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return {expected_value} (as inserted nonepileptic_seizure_type=={seizure_type_answer}). Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_uncertain(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single uncertain epileptic Episode queryset returns correct expected output, with a completed episode.
    """
    expected_value = 11  # 5 for incomplete epileptic episode, ++6 for uncertain episode base value incomplete fields

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__common_fields=True,
        **{
            "registration__multiaxial_diagnosis__episode__epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[
                2
            ][
                0
            ],
        },
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value == expected_value
    ), f"Single completely filled uncertain epileptic Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return {expected_value}. Instead, returned {return_value}"


@pytest.mark.django_db
def test_total_fields_expected_multiaxial_diagnosis_episode_fields(
    e12_case_factory, GOSH
):
    """
    Tests total_fields_expected(multiaxial_diagnosis) returns correct expected output, with a completed Focal Onset episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_focal_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    # Multiaxial diagnosis fields minimum == 7 ++ focal onset episode fields == 8
    expected_value = 15
    return_value = total_fields_expected(multiaxial_diagnosis)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(multiaxial_diagnosis) with fully completed Focal Onset episode should return {expected_value}, instead returned {return_value}"


@pytest.mark.django_db
def test_total_fields_expected_multiaxial_diagnosis_syndrome_fields(
    e12_case_factory, GOSH, e12_syndrome_factory
):
    """
    Tests total_fields_expected(multiaxial_diagnosis) returns correct expected output, with 3 completed Syndromes. Each syndrome registered has 2 fields.

    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode=None,
        registration__multiaxial_diagnosis__syndrome_present=True,
        registration__multiaxial_diagnosis__syndrome_entity=None,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    # Initial value because Multiaxial diagnosis fields minimum == 7 ++ no episodes == 5
    expected_value = 12

    ADD_SYNDROMES = random.choice([None, True])
    if ADD_SYNDROMES is not None:
        # Create 3 syndromes
        SYNDROMES_LIST = SyndromeEntity.objects.all()[:3]

        for i in range(3):
            e12_syndrome_factory(
                multiaxial_diagnosis=multiaxial_diagnosis,
                syndrome_diagnosis_date=date(2023, 1, 1),
                syndrome=SYNDROMES_LIST[i],
            )

            # Each syndrome has 2 fields to complete
            expected_value += 2
    else:
        expected_value += 2  # syndrome_present==True, so minimum value adds 2 expected

    return_value = total_fields_expected(multiaxial_diagnosis)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(multiaxial_diagnosis) with {'3 syndromes registered' if ADD_SYNDROMES else 'syndrome_present==True but no syndromes entered'} expects return value of {expected_value} but received {return_value}"


@pytest.mark.django_db
def test_total_fields_expected_multiaxial_diagnosis_general_fields(
    e12_case_factory, GOSH
):
    """
    Tests total_fields_expected(multiaxial_diagnosis) returns correct expected output, with all general fields all True.

    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__epilepsy_cause_known=True,  # +2
        registration__multiaxial_diagnosis__relevant_impairments_behavioural_educational=True,  # +2
        registration__multiaxial_diagnosis__mental_health_issue_identified=True,  # +1
        registration__multiaxial_diagnosis__global_developmental_delay_or_learning_difficulties=True,  # +1
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    # Initial value because Multiaxial diagnosis fields minimum == 7; ++ no episodes == 5; ++ general_fields all true == 6;
    expected_value = 23

    return_value = total_fields_expected(multiaxial_diagnosis)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(multiaxial_diagnosis) with general fields all True. Expected {expected_value} but got {return_value}"


@pytest.mark.django_db
def test_total_fields_expected_assessment(e12_case_factory, GOSH):
    """
    Tests total_fields_expected(assessment) returns correct expected output, with all general fields all True.
    """

    answer_set = {}
    expected_value = 5  # minimum value when no fields complete
    fields = [
        "consultant_paediatrician_referral_made",
        "paediatric_neurologist_referral_made",
        "childrens_epilepsy_surgical_service_referral_made",
        "epilepsy_specialist_nurse_referral_made",
    ]
    for field in fields:
        answer = random.choice([None, True])

        BASE_KEY_NAME = "registration__assessment__"
        answer_set.update({f"{BASE_KEY_NAME}{field}": answer})

        if answer is not None:
            if field in [
                "epilepsy_specialist_nurse_referral_made",
                "childrens_epilepsy_surgical_service_referral_made",
            ]:
                expected_value += 2
            else:
                expected_value += 3

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        **answer_set,
    )

    assessment = CASE.registration.assessment

    return_value = total_fields_expected(assessment)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(assessment) expected {expected_value} but got {return_value}. Used answers: {answer_set}"


@pytest.mark.django_db
def test_total_fields_expected_investigations(e12_case_factory, GOSH):
    """
    Tests total_fields_expected(investigations) returns correct expected output, with all  fields all True.
    """

    answer_set = {}
    expected_value = 4  # minimum value when no fields complete
    fields = [
        "eeg_indicated",
        "mri_indicated",
    ]
    for field in fields:
        answer = random.choice([None, True])

        BASE_KEY_NAME = "registration__investigations__"
        answer_set.update({f"{BASE_KEY_NAME}{field}": answer})

        if answer is not None:
            expected_value += 2

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        **answer_set,
    )

    investigations = CASE.registration.investigations

    return_value = total_fields_expected(investigations)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(investigations) expected {expected_value} but got {return_value}. Used answers: {answer_set}"


@pytest.mark.django_db
def test_total_fields_expected_registration(e12_case_factory, GOSH):
    """
    Tests total_fields_expected(registration) returns correct expected output, with all  fields all True.
    """

    answer_set = {}

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
    )

    registration = CASE.registration

    expected_value = 3  # minimum value when no fields complete
    return_value = total_fields_expected(registration)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(registration) expected {expected_value} but got {return_value}. Used answers: {answer_set}"


@pytest.mark.django_db
def test_total_fields_expected_management(
    e12_case_factory, e12_anti_epilepsy_medicine_factory, GOSH
):
    """
    Tests total_fields_expected(management) returns correct expected output, with all fields all True.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        date_of_birth=date.today()
        - relativedelta(years=13),  # to test sodium valproate
        organisations__organisation=GOSH,
        sex=SEX_TYPE[2][0],
        registration__management__has_an_aed_been_given=True,
        registration__management__has_rescue_medication_been_prescribed=True,
    )

    management = CASE.registration.management

    # score +3 for medicine present, +2 as valproate in childbearing female
    aed_answers = {
        "medicine_entity": MedicineEntity.objects.get(medicine_name="Sodium valproate"),
        "antiepilepsy_medicine_start_date": date(2023, 1, 1),
        "antiepilepsy_medicine_risk_discussed": True,
        "is_a_pregnancy_prevention_programme_needed": True,
        "is_a_pregnancy_prevention_programme_in_place": True,
        "has_a_valproate_annual_risk_acknowledgement_form_been_completed": True,
    }
    aed = e12_anti_epilepsy_medicine_factory(
        management=management,
        is_rescue_medicine=False,
        **aed_answers,
    )

    # score +3 for medicine present
    rescue_medicine_answers = {
        "medicine_entity": MedicineEntity.objects.get(medicine_name="Levetiracetam"),
        "antiepilepsy_medicine_start_date": date(2023, 1, 1),
        "antiepilepsy_medicine_risk_discussed": True,
    }
    rescue_medicine = e12_anti_epilepsy_medicine_factory(
        management=management,
        is_rescue_medicine=True,
        **rescue_medicine_answers,
    )

    expected_value = 13  # minimum = 5; ++3 for Keppra; ++5 for valproate
    return_value = total_fields_expected(management)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(management) expected {expected_value} but got {return_value}. 13yo girl registered with Valproate AED and Keppra as rescue"
