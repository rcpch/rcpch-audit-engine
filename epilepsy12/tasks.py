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
from epilepsy12.constants import EnumAbstractionLevel
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
def download_kpi_summary_as_csv(cohort=6):
    """
    Asynchronous task to pull data from KPIAggregation tables and store as dataframe for export as CSV
    Accepts cohort as optional param, defaults to 6
    """

    # NATIONAL - SHEET 1
    # create a dataframe with a row for each measure, and column for each of ["Measure", "Percentage", "Numerator", "Denominator"]
    # note rows are named ["1. Paediatrician with expertise","2. Epilepsy specialist nurse","3a. Tertiary involvement","3b. Epilepsy surgery referral","4. ECG","5. MRI","6. Assessment of mental health issues","7. Mental health support","8. Sodium valproate","9a. Comprehensive care planning agreement","9b. Comprehensive care planning content","10. School Individual Health Care Plan"]

    NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")

    national_kpi_aggregation = (
        NationalKPIAggregation.objects.filter(cohort=cohort)
        .values(
            "paediatrician_with_expertise_in_epilepsies_passed",
            "paediatrician_with_expertise_in_epilepsies_total_eligible",
            "epilepsy_specialist_nurse_passed",
            "epilepsy_specialist_nurse_total_eligible",
            "tertiary_input_passed",
            "tertiary_input_total_eligible",
            "epilepsy_surgery_referral_passed",
            "epilepsy_surgery_referral_total_eligible",
            "ecg_passed",
            "ecg_total_eligible",
            "mri_passed",
            "mri_total_eligible",
            "assessment_of_mental_health_issues_passed",
            "assessment_of_mental_health_issues_total_eligible",
            "mental_health_support_passed",
            "mental_health_support_total_eligible",
            "sodium_valproate_passed",
            "sodium_valproate_total_eligible",
            "comprehensive_care_planning_agreement_passed",
            "comprehensive_care_planning_agreement_total_eligible",
            "patient_held_individualised_epilepsy_document_passed",
            "patient_held_individualised_epilepsy_document_total_eligible",
            "patient_carer_parent_agreement_to_the_care_planning_passed",
            "patient_carer_parent_agreement_to_the_care_planning_total_eligible",
            "care_planning_has_been_updated_when_necessary_passed",
            "care_planning_has_been_updated_when_necessary_total_eligible",
            "comprehensive_care_planning_content_passed",
            "comprehensive_care_planning_content_total_eligible",
            "parental_prolonged_seizures_care_plan_passed",
            "parental_prolonged_seizures_care_plan_total_eligible",
            "water_safety_passed",
            "water_safety_total_eligible",
            "first_aid_passed",
            "first_aid_total_eligible",
            "general_participation_and_risk_passed",
            "general_participation_and_risk_total_eligible",
            "service_contact_details_passed",
            "service_contact_details_total_eligible",
            "sudep_passed",
            "sudep_total_eligible",
            "school_individual_healthcare_plan_passed",
            "school_individual_healthcare_plan_total_eligible",
        )
        .first()
    )

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
        "patient_held_individualised_epilepsy_document",
        "patient_carer_parent_agreement_to_the_care_planning",
        "care_planning_has_been_updated_when_necessary",
        "comprehensive_care_planning_content",
        "parental_prolonged_seizures_care_plan",
        "water_safety",
        "first_aid",
        "general_participation_and_risk",
        "service_contact_details",
        "sudep",
        "school_individual_healthcare_plan",
    ]

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

    df = pd.DataFrame.from_dict(final_list)

    return df
