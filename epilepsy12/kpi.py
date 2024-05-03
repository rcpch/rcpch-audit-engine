# Django Imports
from django.apps import apps

# Third party imports
import pandas as pd

# E12 Imports
from epilepsy12.constants import (
    LOCAL_HEALTH_BOARDS,
    INTEGRATED_CARE_BOARDS,
    NHS_ENGLAND_REGIONS,
    OPEN_UK_NETWORKS,
    OPEN_UK_NETWORKS_TRUSTS,
    INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES,
)
from epilepsy12.common_view_functions.aggregate_by import (
    create_KPI_aggregation_dataframe,
    create_reference_dataframe,
    create_kpi_report_row,
)
from epilepsy12.models import (Organisation, Trust, KPI)


def download_kpi_summary_as_csv(cohort):
    """
    Asynchronous task to pull data from KPIAggregation tables and store as dataframe for export as CSV
    Accepts cohort as optional param
    Output - 8 sheets of .xlsx structured as follows:
    - Country level
    - HBT level
    - ICB level
    - NHSregion_level
    - Network_level
    - National_level
    - Reference
    - National_comparison
    """

    # The summary only includes some measures
    measures = [
        KPI._meta.get_field('paediatrician_with_expertise_in_epilepsies'),
        KPI._meta.get_field('epilepsy_specialist_nurse'),
        KPI._meta.get_field('tertiary_input'),
        KPI._meta.get_field('epilepsy_surgery_referral'),
        KPI._meta.get_field('ecg'),
        KPI._meta.get_field('mri'),
        KPI._meta.get_field('assessment_of_mental_health_issues'),
        KPI._meta.get_field('mental_health_support'),
        KPI._meta.get_field('sodium_valproate'),
        KPI._meta.get_field('comprehensive_care_planning_agreement'),
        KPI._meta.get_field('comprehensive_care_planning_content'),
        KPI._meta.get_field('school_individual_healthcare_plan'),
    ]

    trusts_from_organisations = Organisation.objects.values('trust').distinct()
    trusts = Trust.objects.filter(id__in=trusts_from_organisations).values()

    # COUNTRY - SHEET 1
    # create a dataframe with a row for each measure of each country, and a column for each of ["Measure", "Percentage", "Numerator", "Denominator"]

    CountryKPIAggregation = apps.get_model("epilepsy12", "CountryKPIAggregation")

    england_kpi_aggregation = (
        CountryKPIAggregation.objects.filter(cohort=cohort, abstraction_relation=1)
        .values()
        .first()
    )

    wales_kpi_aggregation = (
        CountryKPIAggregation.objects.filter(cohort=cohort, abstraction_relation=4)
        .values()
        .first()
    )

    final_list = []
    for measure in measures:
        england_row = create_kpi_report_row(
            "england", measure, england_kpi_aggregation, "Country"
        )
        wales_row = create_kpi_report_row(
            "wales", measure, wales_kpi_aggregation, "Country"
        )

        final_list.append(england_row)
        final_list.append(wales_row)

    country_df = pd.DataFrame.from_dict(final_list)

    # HBT (Trusts & Health Boards) - SHEET 2

    trust_hb_df = create_KPI_aggregation_dataframe(
        "LocalHealthBoardKPIAggregation",
        "ods_code",
        cohort,
        measures,
        "HBT",
        KPI_model2="TrustKPIAggregation",
        abstraction_key_field2="ods_code",
    )

    # ICB (Integrated Care Board) - SHEET 3

    icb_df = create_KPI_aggregation_dataframe(
        "ICBKPIAggregation", "name", cohort, measures, "ICB"
    )

    # NHS region level - SHEET 4

    region_df = create_KPI_aggregation_dataframe(
        "NHSEnglandRegionKPIAggregation",
        "name",
        cohort,
        measures,
        "NHSregion",
        is_regional=True,
    )

    # NETWORKS - SHEET 5

    network_df = create_KPI_aggregation_dataframe(
        "OpenUKKPIAggregation", "boundary_identifier", cohort, measures, "Network"
    )

    # NATIONAL - SHEET 6
    # create a dataframe with a row for each measure, and column for each of ["Measure", "Percentage", "Numerator", "Denominator"]
    # note rows are named ["1. Paediatrician with expertise","2. Epilepsy specialist nurse","3a. Tertiary involvement","3b. Epilepsy surgery referral","4. ECG","5. MRI","6. Assessment of mental health issues","7. Mental health support","8. Sodium valproate","9a. Comprehensive care planning agreement","9b. Comprehensive care planning content","10. School Individual Health Care Plan"]
    # Note that the function create_dataframe is not called here because there is no list of organisations to iterate through

    NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")

    national_kpi_aggregation = (
        NationalKPIAggregation.objects.filter(cohort=cohort, open_access=False)
        .values()
        .first()
    )

    final_list = []
    for measure in measures:
        item = create_kpi_report_row(
            "national", measure, national_kpi_aggregation, "uk"
        )
        item["uk"] = "England and Wales"
        final_list.append(item)

    national_df = pd.DataFrame.from_dict(final_list)

    # REFERENCE - SHEET 7

    reference_df = create_reference_dataframe(
        trusts,
        LOCAL_HEALTH_BOARDS,
        OPEN_UK_NETWORKS_TRUSTS,
        INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES,
    )

    return (
        country_df,
        trust_hb_df,
        icb_df,
        region_df,
        network_df,
        national_df,
        reference_df,
    )
