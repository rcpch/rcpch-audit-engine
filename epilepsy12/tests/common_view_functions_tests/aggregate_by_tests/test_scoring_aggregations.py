"""Tests for aggregate_by.py functions.
"""

# python imports
import pytest
import random
from datetime import date

# 3rd party imports


# E12 imports
from epilepsy12.common_view_functions import (
    cases_aggregated_by_sex,
    cases_aggregated_by_deprivation_score,
    cases_aggregated_by_ethnicity,
    aggregate_all_eligible_kpi_fields,
    get_kpi_value_counts,
    all_registered_cases_for_cohort_and_abstraction_level,
    calculate_kpis,
    calculate_kpi_value_counts_queryset,
    update_kpi_aggregation_model,
    get_filtered_cases_queryset_for,
)
from epilepsy12.models import (
    Organisation,
    Case,
    Registration,
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
    SEX_TYPE,
    DEPRIVATION_QUINTILES,
    ETHNICITIES,
    EnumAbstractionLevel,
)
from epilepsy12.tests.common_view_functions_tests.CreateKPIMetrics import KPIMetric


@pytest.mark.django_db
def test_debug(e12_case_factory):
    """debug"""
    pass
