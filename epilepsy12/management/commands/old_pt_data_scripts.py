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
    return pd.to_datetime(date_series, format='%d/%m/%Y').dt.date

def clean_nhs_number(nhs_num_series):
    return nhs_num_series.str.replace(" ", "")


def load_and_prep_data(csv_path: str) -> list[dict]:
    """Takes in .csv of old patient data, cleans and maps to E12 data model, returns list of dictionaries, where each dictionary is a patient row, keys are column names, values are values."""
    df = (
        pd.read_csv(csv_path)
        .assign(
            nhs_number=lambda _df: clean_nhs_number(
                _df["S01NHSCHINumber"]
            ),
            ethnicity=lambda _df: map_ethnicities(_df["S01Ethnicity"]),
            postcode=lambda _df: (
                _df["S02HomePostcodeOut"] + _df["S02HomePostcodeIn"]
            ).str.replace(" ", ""),
            date_of_birth=lambda _df: map_date(_df["S01DOBDateOnly"]),
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
