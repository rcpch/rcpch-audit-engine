# python imports
import pytest

# 3rd party imports
from django.apps import apps

# E12 imports
from epilepsy12.common_view_functions import (
    calculate_kpi_value_counts_queryset,
    update_kpi_aggregation_model,
    get_filtered_cases_queryset_for,
    get_abstraction_model_from_level,
)
from epilepsy12.models import (
    Organisation,
    NationalKPIAggregation,
)
from epilepsy12.constants import (
    EnumAbstractionLevel,
)
from .helpers import _clean_cases_from_test_db, _register_kpi_scored_cases


@pytest.mark.parametrize(
    "abstraction_level, abstraction_codes, ods_codes",
    [
        (
            EnumAbstractionLevel.ORGANISATION,
            ["RGT01", "RQM01"],
            ["RGT01", "RQM01"],
        ),
        (
            EnumAbstractionLevel.TRUST,
            ["RGT", "RQM"],
            ["RGT01", "RQM01"],
        ),
        (
            EnumAbstractionLevel.LOCAL_HEALTH_BOARD,
            ["W11000028", "W11000031"],
            ["7A6AV", "7A6G9", "7A3LW", "7A3C7"],
        ),
        (
            EnumAbstractionLevel.ICB,
            ["E54000056", "E54000027"],
            ["RGT01", "RGN90", "R1K02", "RQM01"],
        ),
        (
            EnumAbstractionLevel.NHS_ENGLAND_REGION,
            ["E40000007", "E40000003"],
            ["RGT01", "RGN90", "R1K02", "RQM01"],
        ),
        (
            EnumAbstractionLevel.OPEN_UK,
            ["EPEN", "NTPEN"],
            ["RGT01", "RC979", "RAL26", "RAJ12"],
        ),
        (
            EnumAbstractionLevel.COUNTRY,
            ["E92000001", "W92000004"],
            ["RGT01", "RCF22", "7A2AJ", "7A6BJ"],
        ),
        (
            EnumAbstractionLevel.NATIONAL,
            ["England", "Wales"],
            ["RGT01", "RCF22", "7A2AJ", "7A6BJ"],
        ),
    ],
)
@pytest.mark.django_db
def test_update_kpi_aggregation_model_all_levels(
    abstraction_level, abstraction_codes, ods_codes, e12_case_factory
):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_all_levels`. See those docstrings for details.
    """

    # CONSTANTS
    kpis_tested = [
        "ecg",
        "mental_health_support",
    ]

    # Clean
    _clean_cases_from_test_db()

    kpi_scores_expected = {
        "ecg_passed": 10,
        "ecg_total_eligible": 20,
        "ecg_ineligible": 10,
        "ecg_incomplete": 10,
        "mental_health_support_passed": 10,
        "mental_health_support_total_eligible": 20,
        "mental_health_support_ineligible": 10,
        "mental_health_support_incomplete": 10,
    }
    expected_scores = {code: kpi_scores_expected for code in abstraction_codes}

    _register_kpi_scored_cases(
        e12_case_factory,
        ods_codes=ods_codes,
        num_cases=(
            5
            if abstraction_level
            not in [
                EnumAbstractionLevel.ORGANISATION,
                EnumAbstractionLevel.TRUST,
            ]
            else 10
        ),
    )

    # PERFORM AGGREGATIONS AND UPDATE AGGREGATION MODEL
    for code in ods_codes:
        organisation = Organisation.objects.get(ods_code=code)

        # Get filtered cases
        filtered_cases = get_filtered_cases_queryset_for(
            organisation=organisation,
            abstraction_level=abstraction_level,
            cohort=6,
        )

        # Get value counts
        value_counts = calculate_kpi_value_counts_queryset(
            filtered_cases=filtered_cases,
            abstraction_level=abstraction_level,
            kpis=kpis_tested,
        )

        # ACTION: run update kpi agg model fn
        update_kpi_aggregation_model(
            cohort=6,
            kpi_value_counts=value_counts,
            abstraction_level=abstraction_level,
        )

    # ASSERTION
    if abstraction_level == EnumAbstractionLevel.NATIONAL:
        output = NationalKPIAggregation.objects.get(cohort=6).get_value_counts_for_kpis(
            kpis_tested
        )

        expected_scores = {
            "ecg_passed": 20,
            "ecg_total_eligible": 40,
            "ecg_ineligible": 20,
            "ecg_incomplete": 20,
            "mental_health_support_passed": 20,
            "mental_health_support_total_eligible": 40,
            "mental_health_support_ineligible": 20,
            "mental_health_support_incomplete": 20,
        }

        assert output == expected_scores

    else:
        abstraction_kpi_aggregation_model_name = get_abstraction_model_from_level(
            enum_abstraction_level=abstraction_level
        )["kpi_aggregation_model"]
        abstraction_kpi_aggregation_model = apps.get_model(
            "epilepsy12", abstraction_kpi_aggregation_model_name
        )

        abstraction_entity_model_name = get_abstraction_model_from_level(
            enum_abstraction_level=abstraction_level
        )["abstraction_entity_model"]
        abstraction_entity_model = apps.get_model(
            "epilepsy12", abstraction_entity_model_name
        )

        for abstraction_relation_code in expected_scores:
            abstraction_relation_instance_key = abstraction_level.value.split("__")[-1]

            abstraction_relation_instance = abstraction_entity_model.objects.filter(
                **{abstraction_relation_instance_key: abstraction_relation_code}
            ).first()

            kpi_aggregation_model_instance = (
                abstraction_kpi_aggregation_model.objects.get(
                    abstraction_relation=abstraction_relation_instance, cohort=6
                )
            )

            output = kpi_aggregation_model_instance.get_value_counts_for_kpis(
                kpis_tested
            )

            assert output == expected_scores[abstraction_relation_code]
