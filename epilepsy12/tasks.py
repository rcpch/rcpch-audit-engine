# Python Imports
from typing import Literal, Union
from pprint import pprint

# Django Imports
from django.utils.html import strip_tags
from django.core.mail import send_mail, BadHeaderError

# Third party imports
import nhs_number
from celery import shared_task, Celery

# E12 Imports
from .general_functions import (
    get_current_cohort_data,
)
from epilepsy12.constants import EnumAbstractionLevel
from epilepsy12.common_view_functions.aggregate_by import update_all_kpi_agg_models
from epilepsy12.management.commands.old_pt_data_scripts import load_and_prep_data
from epilepsy12.general_functions.postcode import is_valid_postcode
from epilepsy12.models import Organisation, Case, Site


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
        cohort = get_current_cohort_data()["cohort"]

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
            from_email="admin@epilepsy12.rcpch.tech",
            recipient_list=recipients,
            fail_silently=False,
            message=strip_tags(message),
            html_message=message,
        )
    except Exception:
        raise BadHeaderError



def insert_old_pt_data(csv_path: str = "data.csv"):
    """Seed function to read in Netsolving patient data and insert those Cases inside Epilepsy12."""

    print(
        "\033[33m",
        "Running clean and conversion of old patient data...",
        "\033[33m",
    )

    data_for_db = load_and_prep_data(csv_path=csv_path)

    print(
        "\033[33m",
        "Success! Inserting records into db...",
        "\033[33m",
    )

    cases_to_create = []
    sites_to_create = []

    current_nhs_numbers = set(Case.objects.all().values_list("nhs_number", flat=True))

    seeding_error_report = {}
    total_records = len(data_for_db)
    for ix, record in enumerate(data_for_db):
        print("-" * 10, f"On Record {ix} / {total_records-1}", "-" * 10)
        # Validation steps
        if not nhs_number.is_valid(record["nhs_number"]):
            reason = "Invalid NHS number"
            print(
                f'Record: {record["nhs_number"]} - { reason } - Skipping insertion...'
            )
            seeding_error_report[f"{ix}-ERROR"] = {
                "reason": reason,
                "record": record,
            }
            continue

        if not is_valid_postcode(record["postcode"]):
            reason = "Invalid postcode"
            print(
                f'Record: {record["nhs_number"]} - { reason } - Skipping insertion...'
            )
            seeding_error_report[f"{ix}-ERROR"] = {
                "reason": reason,
                "record": record,
            }
            continue

        # If the Case already exists, we delete as we later re-insert the most recent record
        if record["nhs_number"] in current_nhs_numbers:
            found_duplicate_case = Case.objects.filter(
                nhs_number=record["nhs_number"]
            ).first()
            print(f"{found_duplicate_case.nhs_number} already exists. Deleting...")
            seeding_error_report[f"{ix}-INFO-Case"] = {
                "reason": f"{found_duplicate_case.nhs_number} Record already exists. Deleted and re-inserted.",
                "record": record,
            }

            # This Case should also have the Site. If associated Site already exists, we delete as we later create a fresh one
            duplicate_site = Site.objects.filter(case=found_duplicate_case)
            if duplicate_site.exists():
                found_duplicate_site = duplicate_site.first()
                print(f"{found_duplicate_site} already exists. Deleting...")
                seeding_error_report[f"{ix}-INFO-Site"] = {
                    "reason": f"{found_duplicate_site} already exists. Deleted and re-inserted.",
                    "record": record,
                }

                found_duplicate_site.delete()

            # Delete this last as required for the Site deletion
            found_duplicate_case.delete()

        inserted_case = Case(
            locked=False,
            nhs_number=record["nhs_number"],
            first_name=record["first_name"],
            surname=record["surname"],
            sex=record["sex"],
            date_of_birth=record["date_of_birth"],
            postcode=record["postcode"],
            ethnicity=record["ethnicity"],
        )

        cases_to_create.append(inserted_case)

        # Get organisation
        try:
            organisation = Organisation.objects.get(ods_code=record["OrganisationCode"])
        except Exception as e:
            print(
                f'Couldn\'t find organisation for {record["OrganisationCode"]}. Skipping {record["nhs_number"]}. Error: {e}'
            )
            seeding_error_report[f"{ix}-ERROR"] = {
                "reason": f"Organisation {record['OrganisationCode']} could not be found. Related Site for {inserted_case.nhs_number} was not created.",
                "record": record,
            }
            continue

        # allocate the child to the organisation supplied as primary E12 centre
        inserted_site = Site(
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_primary_centre_of_epilepsy_care=True,
            organisation=organisation,
            case=inserted_case,
        )

        sites_to_create.append(inserted_site)

        print(f"Added {inserted_case.nhs_number} for creation in db.")

    print(f"Creating {len(cases_to_create)} Cases...")
    Case.objects.bulk_create(cases_to_create)
    print(f"Creating {len(sites_to_create)} Sites...")
    Site.objects.bulk_create(sites_to_create)

    # .bulk_create() does not call Case.save() which calculates and saves the index_of_multiple_deprivation_quintile. So do it manually
    print("Saving all Cases to calculate IMD...")
    total_cases_to_save = Case.objects.all().count()
    for ix, case_to_save in enumerate(Case.objects.all()):
        print(f"Saving Case {ix+1} of {total_cases_to_save}...")
        case_to_save.save()

    print("ALL ERRORS: ")
    pprint(seeding_error_report)


@shared_task
def async_insert_old_pt_data(csv_path: str = "data.csv"):
    insert_old_pt_data(csv_path=csv_path)

@shared_task
def hello():
    """
    THIS IS A SCHEDULED TASK THAT IS CALLED AT 06:00 EVERY DAY
    THE CRON DATE/FREQUENCY IS SET IN SETTING.PY
    """
    print("Hello Epilepsy12!")
