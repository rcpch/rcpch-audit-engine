"""
These scripts clean old patient data csv and convert into records which can be seeded into E12 db.
"""

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from epilepsy12.models import (
    LocalHealthBoard,
    Organisation,
    Trust,
)


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
        df.loc[df['SiteName'] == hospital, 'SiteCode'] = new_code

    return df['SiteCode']




def clean_nhs_number(nhs_num_series):
    return nhs_num_series.str.replace(" ", "")


def load_and_prep_data(csv_path: str) -> list[dict]:
    """Takes in .csv of old patient data, cleans and maps to E12 data model, returns list of dictionaries, where each dictionary is a patient row, keys are column names, values are values."""
    print(pd.read_csv(csv_path).dtypes)

    df = (
        pd.read_csv(csv_path)
        .astype({"s01nhschinumber": "string"})
        .assign(
            nhs_number=lambda _df: clean_nhs_number(_df["s01nhschinumber"]),
            ethnicity=lambda _df: map_ethnicities(_df["s01ethnicity"]),
            postcode=lambda _df: (
                _df["s02homepostcodeout"] + _df["s02homepostcodein"]
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
                local_health_board=record_parent_org
            ).first()

        else:
            record_parent_org = Trust.objects.get(ods_code=record_ods_code)
            default_organisation = Organisation.objects.filter(
                trust=record_parent_org
            ).first()

    except Exception as e:
        print(
            f"Error getting Trust for {record_ods_code=}: {e}. Skipping insertion of {record}"
        )

    return default_organisation, record_ods_code, record_parent_org
