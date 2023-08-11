from typing import Literal

from .models import Organisation, KPIAggregation
from .common_view_functions import (
    all_registered_cases_for_cohort_and_abstraction_level,
    aggregate_all_eligible_kpi_fields,
)
from .general_functions import get_current_cohort_data


def aggregate_kpis_for_each_level_of_abstraction_by_organisation_asynchronously(
    organisation_id: str, kpi_measure=None, open_access: bool = False
):
    """
    Reporting function.
    Selects children according to each level of abstraction ('organisation', 'trust', 'icb', 'open_uk', 'nhs_region', 'country', 'national')
    The KPIs for each child are then aggregated and results persisted
    """

    # get the latest cohort
    cohort_data = get_current_cohort_data()

    # get the organisation instance
    organisation = Organisation.objects.get(pk=organisation_id)

    # get all children by level of abstraction
    all_scored_completed_cases_in_current_cohort_by_organisation = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="organisation",
        )
    )

    all_scored_completed_cases_in_current_cohort_by_trust_or_lhb = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="trust",
        )
    )

    all_scored_completed_cases_in_current_cohort_by_icb = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="icb",
        )
    )

    all_scored_completed_cases_in_current_cohort_by_nhs_region = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="nhs_region",
        )
    )

    all_scored_completed_cases_in_current_cohort_by_open_uk_region = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="open_uk",
        )
    )

    all_scored_completed_cases_in_current_cohort_by_country = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="country",
        )
    )

    all_scored_completed_cases_in_current_cohort_by_national = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="national",
        )
    )

    # aggregate the kpis by level of abstraction and persist the results in a table
    organisation_kpis = aggregate_all_eligible_kpi_fields(
        filtered_cases=all_scored_completed_cases_in_current_cohort_by_organisation,
        kpi_measure=kpi_measure,
    )
    trust_kpis = aggregate_all_eligible_kpi_fields(
        filtered_cases=all_scored_completed_cases_in_current_cohort_by_trust_or_lhb,
        kpi_measure=kpi_measure,
    )
    icb_kpis = aggregate_all_eligible_kpi_fields(
        filtered_cases=all_scored_completed_cases_in_current_cohort_by_icb,
        kpi_measure=kpi_measure,
    )
    nhs_kpis = aggregate_all_eligible_kpi_fields(
        filtered_cases=all_scored_completed_cases_in_current_cohort_by_nhs_region,
        kpi_measure=kpi_measure,
    )
    open_uk_kpis = aggregate_all_eligible_kpi_fields(
        filtered_cases=all_scored_completed_cases_in_current_cohort_by_open_uk_region,
        kpi_measure=kpi_measure,
    )
    country_kpis = aggregate_all_eligible_kpi_fields(
        filtered_cases=all_scored_completed_cases_in_current_cohort_by_country,
        kpi_measure=kpi_measure,
    )
    national_kpis = aggregate_all_eligible_kpi_fields(
        filtered_cases=all_scored_completed_cases_in_current_cohort_by_national,
        kpi_measure=kpi_measure,
    )

    # update each aggregated object with the open_access flag
    organisation_kpis.update(
        {"abstraction_level": "organisation", "open_access": open_access}
    )
    trust_kpis.update({"abstraction_level": "trust", "open_access": open_access})
    icb_kpis.update({"abstraction_level": "icb", "open_access": open_access})
    nhs_kpis.update({"abstraction_level": "nhs_region", "open_access": open_access})
    open_uk_kpis.update({"abstraction_level": "open_uk", "open_access": open_access})
    country_kpis.update({"abstraction_level": "country", "open_access": open_access})
    national_kpis.update({"abstraction_level": "national", "open_access": open_access})

    # store the results in KPIAggregation model
    persist_aggregation_results_for_abstraction_level(
        results=organisation_kpis,
        abstraction_level="organisation",
    )
    persist_aggregation_results_for_abstraction_level(
        results=trust_kpis, abstraction_level="trust"
    )
    persist_aggregation_results_for_abstraction_level(
        results=icb_kpis, abstraction_level="icb"
    )
    persist_aggregation_results_for_abstraction_level(
        results=nhs_kpis,
        abstraction_level="nhs_region",
    )
    persist_aggregation_results_for_abstraction_level(
        results=open_uk_kpis,
        abstraction_level="open_uk",
    )
    persist_aggregation_results_for_abstraction_level(
        results=country_kpis,
        abstraction_level="country",
    )
    persist_aggregation_results_for_abstraction_level(
        results=national_kpis,
        abstraction_level="national",
    )


def persist_aggregation_results_for_abstraction_level(
    results: dict,
    abstraction_level: Literal[
        "organisation", "trust", "icb", "nhs_region", "open_uk", "country", "national"
    ] = "organisation",
):
    """
    Private function to store the aggregation results in KPI_Aggregation results table
    """

    if KPIAggregation.objects.filter(abstraction_level=abstraction_level).exists():
        KPIAggregation.objects.filter(abstraction_level=abstraction_level).update(
            **results
        )
    else:
        KPIAggregation.objects.create(**results, abstraction_level=abstraction_level)
