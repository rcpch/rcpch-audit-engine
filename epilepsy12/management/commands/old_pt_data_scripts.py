from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd


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


def clean_and_validate_nhs_number(nhs_num_series):
    # TODO: validate nhs nums
    return nhs_num_series.str.replace(" ", "")


def validate_postcodes():
    # TODO: validate postcodes
    pass


def load_and_prep_data(csv_path:str) -> list[dict]:
    """Takes in .csv of old patient data, cleans and maps to E12 data model, returns list of dictionaries, where each dictionary is a patient row, keys are column names, values are values."""
    df = (
        pd.read_csv(csv_path)
        .assign(
            nhs_number=lambda _df: clean_and_validate_nhs_number(
                _df["S01NHSCHINumber"]
            ),
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
