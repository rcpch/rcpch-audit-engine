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
import random

# Django imports

# E12 imports
from epilepsy12.models import (
    Episode,
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
def test_count_episode_fields(e12_case_factory, GOSH):
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
def test_total_fields_expected_multiaxial_diagnosis_episode_fields(
    e12_case_factory, GOSH
):
    """
    Tests total_fields_expected(multiaxia_diagnosis) returns correct expected output, with a completed Focal Onset episode.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
        registration__multiaxial_diagnosis__episode__complete_episode_focal_onset_seizure=True,
    )

    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

    # Initial minimal value. Multiaxial diagnosis fields minimum == 7 ++ focal onset episode fields == 8
    return_value = total_fields_expected(multiaxial_diagnosis)
    expected_value = 15

    assert return_value == expected_value, f"total_fields_expected(multiaxial_diagnosis) with fully completed Focal Onset episode should return {expected_value}, instead returned {return_value}"
