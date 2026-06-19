"""Tests for `total_fields_expected` fn and `scoreable_fields_for_model_class_name` helper fn.

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
    SyndromeList,
    Medicine,
)
from epilepsy12.common_view_functions.recalculate_form_generate_response import (
    completed_fields,
    number_of_completed_fields_in_related_models,
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
from epilepsy12.models_folder.management import Management
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
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_focal_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value
        == 7  # reduced from 8 as the episode description is nolonger a mandatory field: see issue #1015
    ), f"Single completely filled Focal Onset Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return 7. Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_epileptic_generalised_onset(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single Episode queryset returns correct expected output, with a completed episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_generalised_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value
        == 7  # reduced from 8 as the episode description is nolonger a mandatory field: see issue #1015
    ), f"Single completely filled Generalised Onset Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return 7. Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_epileptic_unclassified_onset(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single Episode queryset returns correct expected output, with a completed episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_unclassified_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value
        == 6  # reduced from 7 as the episode description is nolonger a mandatory field: see issue #1015
    ), f"Single completely filled unclassified Onset Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return 6. Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_epileptic_unknown_onset(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single Episode queryset returns correct expected output, with a completed episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_unknown_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    episode_queryset = Episode.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)

    return_value = count_episode_fields(episode_queryset)

    assert (
        return_value
        == 6  # reduced from 7 as the episode description is nolonger a mandatory field: see issue #1015
    ), f"Single completely filled unknown Onset Episode ({episode_queryset=}) inserted into count_episode_fields() fn. Should return 6. Instead, returned {return_value}"


@pytest.mark.django_db
def test_count_episode_fields_nonepileptic(e12_case_factory, GOSH):
    """
    Tests count_episode_fields with single non epileptic Episode queryset returns correct expected output, with a completed episode.
    """
    expected_value = 10  # 4 for incomplete epileptic episode, ++6 for non epileptic episode base value incomplete fields - not incomplete epileptic episode now reduced to 4 as the episode description is nolonger a mandatory field: see issue #1015

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
        first_name=f"temp_child_{GOSH.name}",
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
    expected_value = 10  # 4 for incomplete epileptic episode, ++6 for uncertain episode base value incomplete fields - incomplete epileptic episode now reduced to 4 as the episode description is nolonger a mandatory field: see issue #1015

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
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
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_focal_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    # Multiaxial diagnosis fields minimum == 7 ++ focal onset episode fields == 7 :  focal onset fields reduced to 7 as the episode description is nolonger a mandatory field: see issue #1015
    expected_value = 14
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
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode=None,
        registration__multiaxial_diagnosis__syndrome_present=True,
        registration__multiaxial_diagnosis__syndrome_entity=None,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    # Initial value because Multiaxial diagnosis fields minimum == 7 ++ no episodes == 5
    expected_value = 12

    ADD_SYNDROMES = random.choice([True])
    if ADD_SYNDROMES is not None:
        # Create 3 syndromes
        SYNDROMES_LIST = SyndromeList.objects.all()[:3]

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
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__epilepsy_cause_known=True,  # +2
        registration__multiaxial_diagnosis__relevant_impairments_behavioural_educational=True,  # +2
        registration__multiaxial_diagnosis__mental_health_issue_identified=True,  # +1
        registration__multiaxial_diagnosis__global_developmental_delay_or_learning_difficulties=True,  # +1
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    # Initial value because Multiaxial diagnosis fields minimum == 6; ++ no episodes == 5; ++ general_fields all true == 6;
    expected_value = 22  # see issue #1125: epilepsy_cause nolonger mandatory

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
        first_name=f"temp_child_{GOSH.name}",
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
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        **answer_set,
    )

    investigations = CASE.registration.investigations

    return_value = total_fields_expected(investigations)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(investigations) expected {expected_value} but got {return_value}. Used answers: {answer_set}"


@pytest.mark.django_db
def test_total_fields_expected_investigations_cohort8_no_genome_answer(
    e12_case_factory, GOSH
):
    """
    Tests total_fields_expected(investigations) for cohort 8 when genome_sequencing_requested
    has not been answered yet. Should add 1 for the genome_sequencing_requested field itself.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
    )

    CASE.registration.first_paediatric_assessment_date = date(2025, 1, 1)
    CASE.registration.save()

    assert CASE.registration.cohort == 8

    investigations = CASE.registration.investigations

    # 4 base fields + 1 for genome_sequencing_requested = 5
    expected_value = 5
    return_value = total_fields_expected(investigations)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(investigations) cohort 8, genome not answered: expected {expected_value} but got {return_value}"


@pytest.mark.django_db
def test_total_fields_expected_investigations_cohort8_genome_requested_true(
    e12_case_factory, GOSH
):
    """
    Tests total_fields_expected(investigations) for cohort 8 when genome_sequencing_requested
    is True but no individual test statuses have been set. Should add fields for the 3 test statuses.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__investigations__genome_sequencing_requested=True,
    )

    CASE.registration.first_paediatric_assessment_date = date(2025, 1, 1)
    CASE.registration.save()

    assert CASE.registration.cohort == 8

    investigations = CASE.registration.investigations

    # 4 base + 1 genome_sequencing_requested + 3 test statuses = 8
    expected_value = 8
    return_value = total_fields_expected(investigations)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(investigations) cohort 8, genome requested, no test statuses: expected {expected_value} but got {return_value}"


@pytest.mark.parametrize(
    "r14_status, r27_status, r59_status, extra_fields",
    [
        ("N", "N", "N", 0),  # all not requested: no date fields
        ("R", "N", "N", 1),  # one requested: +1 requested_date
        ("A", "N", "N", 2),  # one achieved: +1 requested_date +1 achieved_date
        ("R", "R", "N", 2),  # two requested: +2 requested_dates
        ("R", "R", "R", 3),  # all requested: +3 requested_dates
        ("A", "A", "A", 6),  # all achieved: +3 requested_dates +3 achieved_dates
        ("A", "R", "N", 3),  # mixed: +2 for A (req+ach) +1 for R (req)
    ],
    ids=[
        "all_not_requested",
        "one_requested",
        "one_achieved",
        "two_requested",
        "all_requested",
        "all_achieved",
        "mixed_statuses",
    ],
)
@pytest.mark.django_db
def test_total_fields_expected_investigations_cohort8_genome_test_statuses(
    e12_case_factory,
    GOSH,
    r14_status,
    r27_status,
    r59_status,
    extra_fields,
):
    """
    Tests total_fields_expected(investigations) for cohort 8 with various genome test statuses.
    Each "R" (Requested) status adds 1 date field (requested_date).
    Each "A" (Achieved) status adds 2 date fields (requested_date + achieved_date).
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__investigations__genome_sequencing_requested=True,
        registration__investigations__r14_test_status=r14_status,
        registration__investigations__r27_test_status=r27_status,
        registration__investigations__r59_test_status=r59_status,
    )

    CASE.registration.first_paediatric_assessment_date = date(2025, 1, 1)
    CASE.registration.save()

    assert CASE.registration.cohort == 8

    investigations = CASE.registration.investigations

    # 4 base + 1 genome_sequencing_requested + 3 test statuses + extra date fields
    expected_value = 8 + extra_fields
    return_value = total_fields_expected(investigations)

    assert return_value == expected_value, (
        f"total_fields_expected(investigations) cohort 8, "
        f"statuses=({r14_status},{r27_status},{r59_status}): "
        f"expected {expected_value} but got {return_value}"
    )


@pytest.mark.django_db
def test_total_fields_expected_investigations_pre_cohort8_ignores_genome(
    e12_case_factory, GOSH
):
    """
    Tests that genome sequencing fields are NOT scored for cohorts below 8,
    even if genome_sequencing_requested is True.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__investigations__genome_sequencing_requested=True,
        registration__investigations__r14_test_status="A",
        registration__investigations__r27_test_status="R",
        registration__investigations__r59_test_status="N",
    )

    # Default factory date gives cohort 6
    assert CASE.registration.cohort < 8

    investigations = CASE.registration.investigations

    # Only 4 base fields, genome fields should not be scored
    expected_value = 4
    return_value = total_fields_expected(investigations)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(investigations) cohort <8 should ignore genome fields: expected {expected_value} but got {return_value}"


@pytest.mark.django_db
def test_total_fields_expected_investigations_cohort8_with_eeg_and_mri(
    e12_case_factory, GOSH
):
    """
    Tests total_fields_expected(investigations) for cohort 8 with EEG, MRI, and genome fields
    all active to verify they combine correctly.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        organisations__organisation=GOSH,
        registration__investigations__eeg_indicated=True,
        registration__investigations__mri_indicated=True,
        registration__investigations__genome_sequencing_requested=True,
        registration__investigations__r14_test_status="A",
        registration__investigations__r27_test_status="R",
        registration__investigations__r59_test_status="N",
    )

    CASE.registration.first_paediatric_assessment_date = date(2025, 1, 1)
    CASE.registration.save()

    assert CASE.registration.cohort == 8

    investigations = CASE.registration.investigations

    # 4 base + 2 eeg + 2 mri + 1 genome_sequencing_requested
    # + 3 test statuses + 2 (A: req+ach) + 1 (R: req) + 0 (N) = 15
    expected_value = 15
    return_value = total_fields_expected(investigations)

    assert (
        return_value == expected_value
    ), f"total_fields_expected(investigations) cohort 8, eeg+mri+genome: expected {expected_value} but got {return_value}"
    """
    Tests total_fields_expected(registration) returns correct expected output, with all  fields all True.
    """

    answer_set = {}

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
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
        first_name=f"temp_child_{GOSH.name}",
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
        "medicine_entity": Medicine.objects.get(medicine_name="Sodium valproate"),
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
        "medicine_entity": Medicine.objects.get(medicine_name="Levetiracetam"),
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


# Test the form total_fields_expected for topiramate or valproate based on the sex and age of the case
# After cohort 6, both topiramate and valproate require pregnancy prevention programme fields to be filled in girls though in the case of topiramate only if she is over 12y.
# For boys no pregnancy prevention programme fields are required for either medicine but valproate still requires the annual risk acknowledgement form to be completed.
# In cohort 6 and below neither medicine requires pregnancy prevention programme fields to be filled only for girls over 12y on valproate. For cohort 6 and below
# the annual risk acknowledgement is not required


# Note the baseline minimum expected fields for management is 5 when an AED has been given.
@pytest.mark.parametrize(
    "age_over_12, medicine, sex, expected_value",
    [
        (True, "777808008", 2, 5 + 5),  # over 12, female, topiramate
        (True, "387481005", 2, 5 + 5),  # over 12, female, valproate
        (False, "777808008", 2, 5 + 4),  # under 12, female, topiramate
        (False, "387481005", 2, 5 + 5),  # under 12, female, valproate
        (True, "777808008", 1, 5 + 4),  # over 12, male, topiramate
        (True, "387481005", 1, 5 + 4),  # over 12, male, valproate
    ],
)
@pytest.mark.django_db
def test_total_fields_expected_topiramate_or_valproate_for_sex_and_age_cohort_7(
    e12_case_factory,
    e12_anti_epilepsy_medicine_factory,
    GOSH,
    age_over_12,
    medicine,
    sex,
    expected_value,
):
    """
    Tests total_fields_expected(management) returns correct expected output, with all fields all True.
    """
    if age_over_12:
        dob = date(2024, 5, 1) - relativedelta(years=13)
    else:
        dob = date(2024, 5, 1) - relativedelta(years=10)

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        date_of_birth=dob,
        organisations__organisation=GOSH,
        sex=SEX_TYPE[sex][0],
    )

    CASE.registration.first_paediatric_assessment_date = date(2024, 5, 1)
    CASE.registration.cohort = 7
    CASE.registration.management.has_an_aed_been_given = True
    CASE.registration.save()

    # score +3 for medicine present, +2 as topiramate in childbearing female
    if (
        (age_over_12 and medicine == "777808008") or (medicine == "387481005")
    ) and sex == 2:
        aed_answers = {
            "medicine_entity": Medicine.objects.get(conceptId=medicine),
            "antiepilepsy_medicine_start_date": date(2024, 6, 1),
            "antiepilepsy_medicine_risk_discussed": True,
            "is_a_pregnancy_prevention_programme_needed": True,
            "is_a_pregnancy_prevention_programme_in_place": True,
            "has_a_valproate_annual_risk_acknowledgement_form_been_completed": True,
        }
    else:
        aed_answers = {
            "medicine_entity": Medicine.objects.get(conceptId=medicine),
            "antiepilepsy_medicine_start_date": date(2024, 6, 1),
            "antiepilepsy_medicine_risk_discussed": True,
            "is_a_pregnancy_prevention_programme_needed": None,
            "is_a_pregnancy_prevention_programme_in_place": None,
            "has_a_valproate_annual_risk_acknowledgement_form_been_completed": True,
        }

    e12_anti_epilepsy_medicine_factory(
        management=CASE.registration.management,
        is_rescue_medicine=False,
        **aed_answers,
    )

    return_value = total_fields_expected(CASE.registration.management)

    assert (
        CASE.registration.cohort == 7
    ), "Cohort should be 7 for first paediatric assessment date of 2024-05-01"

    # Calculate age at the assessment date, not at current time
    assessment_date = CASE.registration.first_paediatric_assessment_date
    age_at_assessment = CASE.age_days(today_date=assessment_date)

    if age_over_12:
        assert age_at_assessment > (
            12 * 365.25
        ), f"Case should be over 12 years old at assessment date {assessment_date}, but is {age_at_assessment/365.25} years old"
    else:
        assert age_at_assessment < (
            12 * 365.25
        ), f"Case should be under 12 years old at assessment date {assessment_date}, but is {age_at_assessment/365.25} years old"
    assert (
        CASE.sex == sex
    ), f"Case should be {SEX_TYPE[sex][1]}, but is {SEX_TYPE[CASE.sex][1]}"

    assert (
        return_value == expected_value
    ), f"total_fields_expected(management) expected {expected_value} but got {return_value}. >12yo girl registered with Topiramate AED"


@pytest.mark.parametrize(
    "age_over_12, medicine, sex, expected_value",
    [
        (True, "777808008", 2, 5 + 3),  # over 12, female, topiramate
        (
            True,
            "387481005",
            2,
            5 + 5,
        ),  # over 12, female, valproate (needs annual risk acknowledgement and pregnancy prevention programme)
        (False, "777808008", 2, 5 + 3),  # under 12, female, topiramate
        (False, "387481005", 2, 5 + 3),  # under 12, female, valproate
        (True, "777808008", 1, 5 + 3),  # over 12, male, topiramate
        (True, "387481005", 1, 5 + 3),  # over 12, male, valproate
    ],
)
@pytest.mark.django_db
def test_total_fields_expected_topiramate_or_valproate_for_sex_and_age_cohort_6(
    e12_case_factory,
    e12_anti_epilepsy_medicine_factory,
    GOSH,
    age_over_12,
    medicine,
    sex,
    expected_value,
):
    """
    Tests total_fields_expected(management) returns correct expected output, with all fields all True.
    """
    if age_over_12:
        dob = date(2023, 2, 1) - relativedelta(years=13)
    else:
        dob = date(2023, 2, 1) - relativedelta(years=9)

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        date_of_birth=dob,
        organisations__organisation=GOSH,
        sex=SEX_TYPE[sex][0],
    )

    CASE.registration.first_paediatric_assessment_date = date(2023, 5, 1)
    CASE.registration.cohort = 6
    CASE.registration.management.has_an_aed_been_given = True
    CASE.registration.save()

    # score +3 for medicine present, +2 as topiramate in childbearing female
    if age_over_12 and medicine == "387481005" and sex == 2:
        aed_answers = {
            "medicine_entity": Medicine.objects.get(conceptId=medicine),
            "antiepilepsy_medicine_start_date": date(2023, 6, 1),
            "antiepilepsy_medicine_risk_discussed": True,
            "is_a_pregnancy_prevention_programme_needed": True,
            "is_a_pregnancy_prevention_programme_in_place": True,
            "has_a_valproate_annual_risk_acknowledgement_form_been_completed": None,
        }
    else:
        aed_answers = {
            "medicine_entity": Medicine.objects.get(conceptId=medicine),
            "antiepilepsy_medicine_start_date": date(2023, 6, 1),
            "antiepilepsy_medicine_risk_discussed": True,
            "is_a_pregnancy_prevention_programme_needed": None,
            "is_a_pregnancy_prevention_programme_in_place": None,
            "has_a_valproate_annual_risk_acknowledgement_form_been_completed": None,
        }

    e12_anti_epilepsy_medicine_factory(
        management=CASE.registration.management,
        is_rescue_medicine=False,
        **aed_answers,
    )

    return_value = total_fields_expected(CASE.registration.management)

    assert (
        CASE.registration.cohort == 6
    ), f"Cohort should be 6 for first paediatric assessment date of 2023-05-01, but got {CASE.registration.cohort}"

    # Calculate age at the assessment date, not at current time
    assessment_date = CASE.registration.first_paediatric_assessment_date
    age_at_assessment = CASE.age_days(today_date=assessment_date)

    if age_over_12:
        assert age_at_assessment > (
            12 * 365.25
        ), f"Case should be over 12 years old at assessment date {assessment_date}, but is {age_at_assessment/365.25} years old"
    else:
        assert age_at_assessment < (
            12 * 365.25
        ), f"Case should be under 12 years old at assessment date {assessment_date}, but is {age_at_assessment/365.25} years old"
    assert (
        CASE.sex == sex
    ), f"Case should be {SEX_TYPE[sex][1]}, but is {SEX_TYPE[CASE.sex][1]}"

    assert (
        return_value == expected_value
    ), f"total_fields_expected(management) expected {expected_value} but got {return_value}. >12yo girl registered with Topiramate AED"


@pytest.mark.django_db
def test_management_valproate_fields_do_not_overcount_when_not_expected(
    e12_case_factory,
    e12_anti_epilepsy_medicine_factory,
    GOSH,
):
    """
    Regression test for Management scoring: completed fields must not exceed expected fields.

    Cohort 6, under-12 female with multiple AEDs (including valproate) should not
    overcount conditional valproate/topiramate fields when those are not expected.
    """
    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.name}",
        date_of_birth=date(2014, 1, 1),
        organisations__organisation=GOSH,
        sex=SEX_TYPE[2][0],
    )

    CASE.registration.first_paediatric_assessment_date = date(2023, 5, 1)
    CASE.registration.cohort = 6
    CASE.registration.management.has_an_aed_been_given = True
    CASE.registration.management.has_rescue_medication_been_prescribed = False
    CASE.registration.management.save()
    CASE.registration.save()

    # Valproate (not expected to require these extra fields in cohort 6 for under-12 girls)
    e12_anti_epilepsy_medicine_factory(
        management=CASE.registration.management,
        is_rescue_medicine=False,
        medicine_entity=Medicine.objects.get(conceptId="387481005"),
        antiepilepsy_medicine_start_date=date(2023, 6, 1),
        antiepilepsy_medicine_risk_discussed=True,
        is_a_pregnancy_prevention_programme_needed=False,
        has_a_valproate_annual_risk_acknowledgement_form_been_completed=True,
        is_a_pregnancy_prevention_programme_in_place=True,
    )

    # Topiramate with conditional fields filled
    e12_anti_epilepsy_medicine_factory(
        management=CASE.registration.management,
        is_rescue_medicine=False,
        medicine_entity=Medicine.objects.get(conceptId="777808008"),
        antiepilepsy_medicine_start_date=date(2023, 6, 1),
        antiepilepsy_medicine_risk_discussed=True,
        is_a_pregnancy_prevention_programme_needed=False,
        has_a_valproate_annual_risk_acknowledgement_form_been_completed=True,
        is_a_pregnancy_prevention_programme_in_place=True,
    )

    # Third non-valproate AED with conditional fields populated
    e12_anti_epilepsy_medicine_factory(
        management=CASE.registration.management,
        is_rescue_medicine=False,
        medicine_entity=Medicine.objects.get(medicine_name="Levetiracetam"),
        antiepilepsy_medicine_start_date=date(2023, 6, 1),
        antiepilepsy_medicine_risk_discussed=True,
        is_a_pregnancy_prevention_programme_needed=False,
        has_a_valproate_annual_risk_acknowledgement_form_been_completed=True,
        is_a_pregnancy_prevention_programme_in_place=True,
    )

    management = CASE.registration.management
    all_completed_fields = completed_fields(
        management
    ) + number_of_completed_fields_in_related_models(management)
    all_expected_fields = total_fields_expected(management)

    assert (
        all_completed_fields <= all_expected_fields
    ), f"Management overcount: completed={all_completed_fields}, expected={all_expected_fields}"
