""" Tests for `total_fields_expected` fn and `scoreable_fields_for_model_class_name` helper fn.
"""

# Python imports
import pytest
from datetime import date
import random

# Django imports

# E12 imports
from epilepsy12.common_view_functions.recalculate_form_generate_response import (
    scoreable_fields_for_model_class_name,
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
