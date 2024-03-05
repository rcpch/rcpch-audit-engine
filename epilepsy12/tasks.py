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
from epilepsy12.constants import EnumAbstractionLevel, TRUSTS, LOCAL_HEALTH_BOARDS
from epilepsy12.common_view_functions.aggregate_by import update_all_kpi_agg_models
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
    Accepts cohort as optional param, defaults to 6
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
        if england_kpi_aggregation[f"{kpi}_total_eligible"] == 0:
            item = {
                "Country": "England",
                "Measure": kpi,
                "Numerator": england_kpi_aggregation[f"{kpi}_passed"],
                "Denominator": england_kpi_aggregation[f"{kpi}_total_eligible"],
                "Percentage": 0
            }
        else:
            item = {
                "Country": "England",
                "Measure": kpi,
                "Numerator": england_kpi_aggregation[f"{kpi}_passed"],
                "Denominator": england_kpi_aggregation[f"{kpi}_total_eligible"],
                "Percentage": england_kpi_aggregation[f"{kpi}_passed"]
                / england_kpi_aggregation[f"{kpi}_total_eligible"]
                * 100,
            }
        final_list.append(item)
        if wales_kpi_aggregation[f"{kpi}_total_eligible"] == 0:
            item = {
            "Country": "Wales",
            "Measure": kpi,
            "Numerator": wales_kpi_aggregation[f"{kpi}_passed"],
            "Denominator": wales_kpi_aggregation[f"{kpi}_total_eligible"],
            "Percentage": 0
            }
        else:
            item = {
                "Country": "Wales",
                "Measure": kpi,
                "Numerator": wales_kpi_aggregation[f"{kpi}_passed"],
                "Denominator": wales_kpi_aggregation[f"{kpi}_total_eligible"],
                "Percentage": wales_kpi_aggregation[f"{kpi}_passed"]
                / wales_kpi_aggregation[f"{kpi}_total_eligible"]
                * 100,
            }
        final_list.append(item)

    country_df = pd.DataFrame.from_dict(final_list)

    
    # HBT (Trusts & Health Boards) - SHEET 2

    TrustKPIAggregation = apps.get_model("epilepsy12", "TrustKPIAggregation")
    HealthBoardKPIAggregation = apps.get_model("epilepsy12", "LocalHealthBoardKPIAggregation")

    # Create a dictionary of trust KPI aggregations for cohorts
    trusts_and_hbs_objects = {}

    for i, hb in enumerate(LOCAL_HEALTH_BOARDS):
        hb_ods = hb["ods_code"]
        hb_uid = i+1
        trusts_and_hbs_objects[f"{hb_ods}"] = HealthBoardKPIAggregation.objects.filter(cohort=cohort, abstraction_relation=hb_uid).values().first()

    for i, trust in enumerate(TRUSTS):
        trust_ods = trust["ods_code"]
        trust_uid = i+1
        trusts_and_hbs_objects[f"{trust_ods}"] = TrustKPIAggregation.objects.filter(cohort=cohort, abstraction_relation=trust_uid).values().first()
    


    # Create dataframe for KPI aggregations for trusts
    # Must catch NoneType errors (ie if no KPI data for a trust)
        
    final_list = []

    for key in trusts_and_hbs_objects:
        trust_object = trusts_and_hbs_objects[key]
        for kpi in measures:
            if trust_object == None:
                item = {
                    "HBT": key,
                    "Measure": kpi,
                    "Numerator": 0,
                    "Denominator": 0,
                    "Percentage": 0
                }
            elif trust_object[f"{kpi}_total_eligible"] == 0:
                item = {
                    "HBT": key,
                    "Measure": kpi,
                    "Numerator": trust_object[f"{kpi}_passed"],
                    "Denominator": trust_object[f"{kpi}_total_eligible"],
                    "Percentage": 0
                }
            else:
                item = {
                    "HBT": key,
                    "Measure": kpi,
                    "Numerator": trust_object[f"{kpi}_passed"],
                    "Denominator": trust_object[f"{kpi}_total_eligible"],
                    "Percentage": trust_object[f"{kpi}_passed"]
                    / trust_object[f"{kpi}_total_eligible"]
                    * 100,
                }
            final_list.append(item)            
        
    trust_hb_df = pd.DataFrame.from_dict(final_list)

    # ICB (Integrated Care Board) - Sheet 3



    # NATIONAL - SHEET 5
    # create a dataframe with a row for each measure, and column for each of ["Measure", "Percentage", "Numerator", "Denominator"]
    # note rows are named ["1. Paediatrician with expertise","2. Epilepsy specialist nurse","3a. Tertiary involvement","3b. Epilepsy surgery referral","4. ECG","5. MRI","6. Assessment of mental health issues","7. Mental health support","8. Sodium valproate","9a. Comprehensive care planning agreement","9b. Comprehensive care planning content","10. School Individual Health Care Plan"]

    NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")

    national_kpi_aggregation = NationalKPIAggregation.objects.filter(cohort=cohort).values().first()

    final_list = []
    for kpi in measures:
        item = {
            "Measure": kpi,
            "Numerator": national_kpi_aggregation[f"{kpi}_passed"],
            "Denominator": national_kpi_aggregation[f"{kpi}_total_eligible"],
            "Percentage": national_kpi_aggregation[f"{kpi}_passed"]
            / national_kpi_aggregation[f"{kpi}_total_eligible"]
            * 100,
        }
        final_list.append(item)

    national_df = pd.DataFrame.from_dict(final_list)

    return trust_hb_df
    # Use ExcelWriter class from pandas to write each dataframe to its own sheet at the end of function

    # with pd.ExcelWriter("kpi_export.xlsx") as writer:
    #     country_df.to_excel(writer, sheet_name="Country_level")
    #     national_df.to_excel(writer, sheet_name="National_level")
