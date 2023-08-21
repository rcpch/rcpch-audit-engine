# python imports
import pytest
import random
from datetime import date

# 3rd party imports


# E12 imports
from epilepsy12.models import Organisation
from epilepsy12.common_view_functions import (
    calculate_kpi_value_counts_queryset,
    get_filtered_cases_queryset_for,
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
            EnumAbstractionLevel.ICB,
            ["QUE", "QRV"],
            ["RGT01", "RYVD9", "RYJ03", "RQM01"],
        ),
        (
            EnumAbstractionLevel.NHS_REGION,
            ["Y61", "Y56"],
            ["RGT01", "RAJ12", "RAL26", "R1K02"],
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
def test_calculate_kpi_value_counts_queryset_all_levels(
    abstraction_level, abstraction_codes, ods_codes, e12_case_factory
):
    """"""

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

    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes, num_cases=5 if abstraction_level not in [EnumAbstractionLevel.ORGANISATION, EnumAbstractionLevel.TRUST] else 10)

    for code in ods_codes:
        organisation = Organisation.objects.get(ODSCode=code)

        filtered_cases = get_filtered_cases_queryset_for(
            organisation=organisation,
            abstraction_level=abstraction_level,
            cohort=6,
        )

        value_counts = calculate_kpi_value_counts_queryset(
            filtered_cases=filtered_cases,
            abstraction_level=abstraction_level,
            kpis=[
                "ecg",
                "mental_health_support",
            ],
        )
        
        print(value_counts)

        for vc in value_counts:
            abstraction_code = vc.pop(f"organisation__{abstraction_level.value}")
            assert vc == expected_scores[abstraction_code]
