# python imports
import pytest
import random
from datetime import date

# 3rd party imports


# E12 imports
from epilepsy12.common_view_functions import (
    calculate_kpi_value_counts_queryset,
    get_filtered_cases_queryset_for,
)

from epilepsy12.constants import (
    EnumAbstractionLevel,
)

from .helpers import _clean_cases_from_test_db, _register_kpi_scored_cases


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_organisation_level(e12_case_factory):
    """This test generates 60 children total at 2 different organisations (30 each), with known KPI scorings. Asserts the value counts function returns the expected KPI value counts.

    NOTE: To simplify the expected score fields, we just use 2 KPIs. This is a valid simplification as the function does not touch KPI scorings - only getting scorings from the model and aggregating. Thus, if it works for 2 kpis (or even 1), it should work for all.
    NOTE: the 2 different organisations (Addenbrooke's Hospital and YSBYTY YSTRAD FAWR [chosen as first and last alphabetically]) are chosen as they differ at each level of abstraction.
    """

    # Clean
    _clean_cases_from_test_db()

    ods_codes = ["RGT01", "RQM01"]
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
    expected_scores = {ods_code: kpi_scores_expected for ods_code in ods_codes}

    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.ORGANISATION, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=EnumAbstractionLevel.ORGANISATION,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{EnumAbstractionLevel.ORGANISATION.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_trust_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at trust level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # ParentOrganisation_ODSCode
    abstraction_codes = ["RGT", "RQM"]
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
    abstraction_level = EnumAbstractionLevel.TRUST

    ods_codes = ["RGT01", "RQM01"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.TRUST, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_icb_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at icb level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # integrated_care_board__ODS_ICB_Code
    abstraction_codes = ["QUE", "QRV"]
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
    abstraction_level = EnumAbstractionLevel.ICB

    ods_codes = ["RGT01", "RQM01"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.ICB, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_nhs_region_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at nhs region level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # nhs_region__NHS_Region_Code
    abstraction_codes = ["Y61", "Y56"]
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
    abstraction_level = EnumAbstractionLevel.NHS_REGION

    ods_codes = ["RGT01", "RQM01"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.NHS_REGION, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_open_uk_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at OPENUK level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # openuk_network__OPEN_UK_Network_Code
    abstraction_codes = ["EPEN", "NTPEN"]
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
    abstraction_level = EnumAbstractionLevel.OPEN_UK

    ods_codes = ["RGT01", "RQM01"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.OPEN_UK, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        ods_code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[ods_code]


@pytest.mark.django_db
def test_calculate_kpi_value_counts_queryset_country_level(e12_case_factory):
    """Same as `test_calculate_kpi_value_counts_queryset_organisation_level` but at country level. See those docstrings for details."""

    # Clean
    _clean_cases_from_test_db()

    # ons_region__ons_country__Country_ONS_Code
    abstraction_codes = ["E92000001", "W92000004"]
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
    abstraction_level = EnumAbstractionLevel.COUNTRY

    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.COUNTRY, cohort=6
    )

    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=[
            "ecg",
            "mental_health_support",
        ],
    )

    for vc in value_counts:
        code = vc.pop(f"organisation__{abstraction_level.value}")
        assert vc == expected_scores[code]
