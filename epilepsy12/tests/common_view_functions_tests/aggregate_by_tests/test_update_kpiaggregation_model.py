# python imports
import pytest

# 3rd party imports


# E12 imports
from epilepsy12.common_view_functions import (
    calculate_kpi_value_counts_queryset,
    update_kpi_aggregation_model,
    get_filtered_cases_queryset_for,
)
from epilepsy12.models import (
    Organisation,
    OrganisationKPIAggregation,
    CountryKPIAggregation,
    ONSCountryEntity,
    OPENUKNetworkEntity,
    NHSRegionKPIAggregation,
    OpenUKKPIAggregation,
    ICBKPIAggregation,
    TrustKPIAggregation,
    NHSRegionEntity,
    IntegratedCareBoardEntity,
)
from epilepsy12.constants import (
    EnumAbstractionLevel,
)
from .helpers import _clean_cases_from_test_db, _register_kpi_scored_cases


@pytest.mark.django_db
def test_update_kpi_aggregation_model_organisation_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level`. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.ORGANISATION
    abstractions = [
        Organisation.objects.get(ODSCode=abstraction_code)
        for abstraction_code in ("RGT01", "7A6AV")
    ]
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

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.ORGANISATION, cohort=6
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
        abstraction_level=EnumAbstractionLevel.ORGANISATION,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = OrganisationKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_trust_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but on Trust level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.TRUST
    abstractions = ("RGT", "7A6")
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

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.TRUST, cohort=6
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
        abstraction_level=EnumAbstractionLevel.TRUST,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = TrustKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_icb_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but at icb level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.ICB

    expected_scores = {
        IntegratedCareBoardEntity.objects.get(ODS_ICB_Code="QUE"): {
            "ecg_passed": 10,
            "ecg_total_eligible": 20,
            "ecg_ineligible": 10,
            "ecg_incomplete": 10,
            "mental_health_support_passed": 10,
            "mental_health_support_total_eligible": 20,
            "mental_health_support_ineligible": 10,
            "mental_health_support_incomplete": 10,
        }
    }

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=abstraction_level, cohort=6
    )

    # Get value counts
    value_counts = calculate_kpi_value_counts_queryset(
        filtered_cases=filtered_cases,
        abstraction_level=abstraction_level,
        kpis=kpis_tested,
    )

    # ACTION: run update kpi agg model fn
    update_kpi_aggregation_model(
        cohort=6, kpi_value_counts=value_counts, abstraction_level=abstraction_level
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = ICBKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_nhs_region_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but at nhs region level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.NHS_REGION
    abstractions = [
        NHSRegionEntity.objects.get(NHS_Region_Code=abstraction_code)
        for abstraction_code in ("Y61", "7A6")
    ]
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

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.NHS_REGION, cohort=6
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
        abstraction_level=EnumAbstractionLevel.NHS_REGION,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = NHSRegionKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_open_uk_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but at openuk level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]

    abstraction_level = EnumAbstractionLevel.OPEN_UK
    abstractions = [
        OPENUKNetworkEntity.objects.get(OPEN_UK_Network_Code=abstraction_code)
        for abstraction_code in ("EPEN", "SWEP")
    ]
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

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.OPEN_UK, cohort=6
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
        abstraction_level=EnumAbstractionLevel.OPEN_UK,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = OpenUKKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )


@pytest.mark.django_db
def test_update_kpi_aggregation_model_country_level(e12_case_factory):
    """Testing the `update_kpi_aggregation_model` fn.

    Similar test setup as `test_calculate_kpi_value_counts_queryset_organisation_level` but at country level. See those docstrings for details.
    """

    # Clean
    _clean_cases_from_test_db()

    # Define constants
    kpis_tested = ["ecg", "mental_health_support"]
    abstraction_level = EnumAbstractionLevel.COUNTRY
    abstractions = [
        ONSCountryEntity.objects.get(Country_ONS_Code=abstraction_code)
        for abstraction_code in ("E92000001", "W92000004")
    ]
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

    # Generate expected scores
    expected_scores = {code: kpi_scores_expected for code in abstractions}

    # Get scored test cases
    ods_codes = ["RGT01", "7A6AV"]
    _register_kpi_scored_cases(e12_case_factory, ods_codes=ods_codes)

    filtered_cases = get_filtered_cases_queryset_for(
        abstraction_level=EnumAbstractionLevel.COUNTRY, cohort=6
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
        abstraction_level=EnumAbstractionLevel.COUNTRY,
    )

    # For each abstraction code, check output is expected
    for abstraction_relation_entity in expected_scores:
        abstraction_kpi_aggregation_model = CountryKPIAggregation.objects.get(
            abstraction_relation=abstraction_relation_entity
        )

        assert (
            abstraction_kpi_aggregation_model.get_value_counts_for_kpis(kpis_tested)
            == expected_scores[abstraction_relation_entity]
        )
