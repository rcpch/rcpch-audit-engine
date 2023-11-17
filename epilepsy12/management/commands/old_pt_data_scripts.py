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
        "WIrish": "C",
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


def from_excel_ordinal(ordinal: float, _epoch0=datetime(1899, 12, 31)) -> date:
    """Thanks to Martijn Pieters: https://stackoverflow.com/questions/29387137/how-to-convert-a-given-ordinal-number-from-excel-to-a-date/29387450#29387450."""
    if ordinal >= 60:
        ordinal -= 1  # Excel leap year bug, 1900 is not a leap year!
    return (_epoch0 + timedelta(days=ordinal)).replace(microsecond=0).date()


def map_dob(dob_series):
    return dob_series.apply(from_excel_ordinal)


def map_sex(sex_series):
    return sex_series.map(
        {
            "M": 1,
            "F": 2,
            "NK": 0,
        }
    )


def clean_nhs_number(nhs_num_series):
    return nhs_num_series.str.replace(" ", "")


def load_and_prep_data(csv_path: str) -> list[dict]:
    """Takes in .csv of old patient data, cleans and maps to E12 data model, returns list of dictionaries, where each dictionary is a patient row, keys are column names, values are values."""
    df = (
        pd.read_csv(csv_path)
        .assign(
            nhs_number=lambda _df: clean_nhs_number(_df["S01NHSCHINumber"]),
            ethnicity=lambda _df: map_ethnicities(_df["S01Ethnicity"]),
            postcode=lambda _df: (
                _df["S02HomePostcodeOut"] + _df["S02HomePostcodeIn"]
            ).str.replace(" ", ""),
            date_of_birth=lambda _df: map_dob(_df["S01DOBDateOnly"]),
            sex=lambda _df: map_sex(_df["S01Gender"]),
            first_name=lambda _df: _df["S01FirstName"].str.strip(),
            surname=lambda _df: _df["S01SurName"].str.strip(),
        )
        .drop(
            columns=[
                "S02HomePostcodeOut",  # mapped to `postcode`
                "S02HomePostcodeIn",  # mapped to `postcode`
                "S01NHSCHINumber",  # mapped to `nhs_number`
                "S01Ethnicity",  # mapped to `ethnicity`
                "S01Gender",  # mapped to `sex`
                "S01DOBDateOnly",  # mapped to `date_of_birth`
                "S01EthnicityOtherSpecify",
                "S01ReferringHospital",
                "S01FirstName",  # mapped to `first_name`
                "S01SurName",  # mapped to `surname`
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

    return default_organisation,record_ods_code,record_parent_org
