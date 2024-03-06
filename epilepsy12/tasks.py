# Python Imports
from typing import Literal, Union
from datetime import date
import logging

# Django Imports
from django.utils.html import strip_tags
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.apps import apps
from django.db.models.aggregates import Sum

# Third party imports
from celery import shared_task
import pandas as pd

# E12 Imports
from .general_functions import cohort_number_from_first_paediatric_assessment_date
from epilepsy12.constants import EnumAbstractionLevel, TRUSTS, LOCAL_HEALTH_BOARDS, INTEGRATED_CARE_BOARDS, NHS_ENGLAND_REGIONS, OPEN_UK_NETWORKS
from epilepsy12.common_view_functions.aggregate_by import create_KPI_aggregation_dataframe, update_all_kpi_agg_models
from epilepsy12.management.commands.old_pt_data_scripts import insert_old_pt_data
from epilepsy12.management.commands.user_scripts import insert_user_data

# Logging setup
logger = logging.getLogger(__name__)


@shared_task
def asynchronously_aggregate_kpis_and_update_models_for_cohort_and_abstraction_level(
    cohort: int = None,
    abstractions: Union[Literal["all"], list[EnumAbstractionLevel]] = "all",
    open_access=False,
):
    """This asynchronous task will run through all Cases for the Cohort, for all abstraction levels, aggregate KPI scores and update each abstraction's KPIAggregation model.
    `cohort` and `abstractions` parameters are optional.
    """
    # If no cohort supplied, automatically get cohort from current datetime
    if cohort is None:
        cohort = cohort_number_from_first_paediatric_assessment_date(date.today())

    # By default, this will update all KPIAggregation models for all levels of abstraction
    update_all_kpi_agg_models(
        cohort=cohort, abstractions=abstractions, open_access=open_access
    )


@shared_task
def asynchronously_send_email_to_recipients(
    recipients: list, subject: str, message: str
):
    """
    Sends emails
    """
    try:
        send_mail(
            subject=subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
            message=strip_tags(message),
            html_message=message,
        )
    except Exception:
        raise BadHeaderError


@shared_task
def async_insert_old_pt_data(csv_path: str = "data.csv"):
    insert_old_pt_data(csv_path=csv_path)


@shared_task
def async_insert_user_data(csv_path: str = "data.csv"):
    insert_user_data(csv_path=csv_path)


@shared_task
def hello():
    """
    THIS IS A SCHEDULED TASK THAT IS CALLED AT 06:00 EVERY DAY
    THE CRON DATE/FREQUENCY IS SET IN SETTING.PY
    """
    logger.debug("0600 cron check task ran successfully")


@shared_task
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

    # Define KPI measures for extraction
    measures = [
        "paediatrician_with_expertise_in_epilepsies",
        "epilepsy_specialist_nurse",
        "tertiary_input",
        "epilepsy_surgery_referral",
        "ecg",
        "mri",
        "assessment_of_mental_health_issues",
        "mental_health_support",
        "sodium_valproate",
        "comprehensive_care_planning_agreement",
        "comprehensive_care_planning_content",
        "school_individual_healthcare_plan",
    ]

    # COUNTRY - SHEET 1
    # create a dataframe with a row for each measure of each country, and a column for each of ["Measure", "Percentage", "Numerator", "Denominator"]
    
    CountryKPIAggregation = apps.get_model("epilepsy12", "CountryKPIAggregation")

    england_kpi_aggregation = (
        CountryKPIAggregation.objects.filter(cohort=cohort, abstraction_relation=1).values().first()
    )

    wales_kpi_aggregation = (
        CountryKPIAggregation.objects.filter(cohort=cohort, abstraction_relation=4).values().first()
    )

    final_list = []
    for kpi in measures:
        item = {
            "Country": "England",
            "Measure": kpi,
            "Percentage": 0 if england_kpi_aggregation[f"{kpi}_total_eligible"] == 0 else
                england_kpi_aggregation[f"{kpi}_passed"]
                / england_kpi_aggregation[f"{kpi}_total_eligible"]
                * 100,
            "Numerator": england_kpi_aggregation[f"{kpi}_passed"],
            "Denominator": england_kpi_aggregation[f"{kpi}_total_eligible"],
        }
        final_list.append(item)
        item = {
        "Country": "Wales",
        "Measure": kpi,
        "Percentage": 0 if wales_kpi_aggregation[f"{kpi}_total_eligible"] == 0 else
            wales_kpi_aggregation[f"{kpi}_passed"]
            / wales_kpi_aggregation[f"{kpi}_total_eligible"]
            * 100,
        "Numerator": wales_kpi_aggregation[f"{kpi}_passed"],
        "Denominator": wales_kpi_aggregation[f"{kpi}_total_eligible"],
        }
        final_list.append(item)

    country_df = pd.DataFrame.from_dict(final_list)

    # HBT (Trusts & Health Boards) - SHEET 2

    trust_hb_df = create_KPI_aggregation_dataframe("LocalHealthBoardKPIAggregation", LOCAL_HEALTH_BOARDS, cohort, measures, KPI_model2="TrustKPIAggregation", constants_list2=TRUSTS)

    # ICB (Integrated Care Board) - SHEET 3

    icb_df = create_KPI_aggregation_dataframe("ICBKPIAggregation", INTEGRATED_CARE_BOARDS, cohort, measures)

    # NHS region level - SHEET 4

    region_df = create_KPI_aggregation_dataframe("NHSEnglandRegionKPIAggregation", NHS_ENGLAND_REGIONS, cohort, measures, is_regional=True)

    # NETWORKS - SHEET 5
        
    network_df = create_KPI_aggregation_dataframe("OpenUKKPIAggregation", OPEN_UK_NETWORKS, cohort, measures)

    # NATIONAL - SHEET 6
    # create a dataframe with a row for each measure, and column for each of ["Measure", "Percentage", "Numerator", "Denominator"]
    # note rows are named ["1. Paediatrician with expertise","2. Epilepsy specialist nurse","3a. Tertiary involvement","3b. Epilepsy surgery referral","4. ECG","5. MRI","6. Assessment of mental health issues","7. Mental health support","8. Sodium valproate","9a. Comprehensive care planning agreement","9b. Comprehensive care planning content","10. School Individual Health Care Plan"]
    # Note that the function create_dataframe is not called here because there is no list of organisations to iterate through

    NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")

    national_kpi_aggregation = NationalKPIAggregation.objects.filter(cohort=cohort).values().first()

    final_list = []
    for kpi in measures:
        item = {
            "Measure": kpi,
            "Percentage": national_kpi_aggregation[f"{kpi}_passed"]
            / national_kpi_aggregation[f"{kpi}_total_eligible"]
            * 100,
            "Numerator": national_kpi_aggregation[f"{kpi}_passed"],
            "Denominator": national_kpi_aggregation[f"{kpi}_total_eligible"],
        }
        final_list.append(item)

    national_df = pd.DataFrame.from_dict(final_list)

    return country_df, trust_hb_df, icb_df, region_df, network_df, national_df