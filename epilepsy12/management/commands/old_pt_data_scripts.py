"""
These scripts clean old patient data csv and convert into records which can be seeded into E12 db.
"""

import pprint

import nhs_number
import pandas as pd

from epilepsy12.models import (
    LocalHealthBoard,
    Organisation,
    Trust,
    Organisation,
    Case,
    Site,
)
from epilepsy12.general_functions.postcode import is_valid_postcode


def map_ethnicities(ethnicities_series):
    ethnicity_mapping = {
        "WBritish": "A",
        "WIrish": "B",
        "WOther": "C",
        "BCaribbean": "M",
        "BAfrican": "N",
        "BOther": "P",
        "AIndian": "H",
        "APakistani": "J",
        "ABangladeshi": "K",
        "AOther": "L",
        "MWBC": "D",
        "MWBA": "E",
        "MWAs": "F",
        "MOther": "G",
        "OChinese": "R",
        "OOther": "S",
        "No": "Z",
        "NK": "Z",
    }

    return ethnicities_series.map(ethnicity_mapping)


def map_sex(sex_series):
    return sex_series.map(
        {
            "M": 1,
            "F": 2,
            "NK": 0,
        }
    )


def map_date(date_series):
    return pd.to_datetime(date_series, format="%d/%m/%Y").dt.date


def map_merged_trusts(df):
    merged_trust_map = {
        "City Hospitals Sunderland NHS Foundation Trust": "R0B",
        "South Tyneside NHS Foundation Trust": "R0B",
        "North Cumbria Integrated Care NHS Foundation Trust": "RNN",
        "Cumbria Partnership NHS Foundation Trust": "RNN",
    }

    # Updating SiteCode based on SiteName. Ugly, but works.
    for hospital, new_code in merged_trust_map.items():
        df.loc[df["SiteName"] == hospital, "SiteCode"] = new_code

    return df["SiteCode"]


def clean_nhs_number(nhs_num_series):
    return nhs_num_series.str.replace(" ", "")


def load_and_prep_data(csv_path: str) -> list[dict]:
    """Takes in .csv of old patient data, cleans and maps to E12 data model, returns list of dictionaries, where each dictionary is a patient row, keys are column names, values are values."""

    df = (
        pd.read_csv(csv_path)
        .astype({"s01nhschinumber": "string"})
        .assign(
            nhs_number=lambda _df: clean_nhs_number(_df["s01nhschinumber"]),
            ethnicity=lambda _df: map_ethnicities(_df["s01ethnicity"]),
            postcode=lambda _df: (
                _df["s02homepostcodeout"].str.strip()
                + _df["s02homepostcodein"].str.strip()
            ).str.replace(" ", ""),
            date_of_birth=lambda _df: map_date(_df["s01dobdateonly"]),
            sex=lambda _df: map_sex(_df["s01gender"]),
            first_name=lambda _df: _df["s01firstname"].str.strip(),
            surname=lambda _df: _df["s01surname"].str.strip(),
        )
        .drop(
            columns=[
                "s02homepostcodeout",  # mapped to `postcode`
                "s02homepostcodein",  # mapped to `postcode`
                "s01nhschinumber",  # mapped to `nhs_number`
                "s01ethnicity",  # mapped to `ethnicity`
                "s01gender",  # mapped to `sex`
                "s01dobdateonly",  # mapped to `date_of_birth`
                "s01ethnicityotherspecify",
                "s01referringhospital",
                "s01firstname",  # mapped to `first_name`
                "s01surname",  # mapped to `surname`
            ]
        )
        .astype({"sex": "int8"})
    )

    # ORGCODE TYPO FIX
    df["OrganisationCode"] = df["OrganisationCode"].replace({"C0X3P": "COX3P"})

    print("Cleaned data:")
    print(df.dtypes)
    print(df.head())

    return df.to_dict(orient="records")


def get_default_org_from_record(record):
    record_ods_code = record["SiteCode"]

    # Get LHB ODS Codes for lookup differentiation
    lhb_ods_codes = set(
        LocalHealthBoard.objects.all().values_list("ods_code", flat=True).distinct()
    )

    try:
        # only supplied parent Organisation, so find the first Organisation belonging to that Parent, and assign it as the default_organisation
        if record_ods_code in lhb_ods_codes:
            record_parent_org = LocalHealthBoard.objects.get(ods_code=record_ods_code)
            default_organisation = Organisation.objects.filter(
                local_health_board=record_parent_org, active=True
            ).first()

        else:
            record_parent_org = Trust.objects.get(ods_code=record_ods_code)
            default_organisation = Organisation.objects.filter(
                trust=record_parent_org, active=True
            ).first()

    except Exception as e:
        print(
            f"Error getting Trust for {record_ods_code=}: {e}. Skipping insertion of {record}"
        )

    return default_organisation, record_ods_code, record_parent_org


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

        if not is_valid_postcode(record["postcode"], is_jersey=False):
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
    print(seeding_error_report)
