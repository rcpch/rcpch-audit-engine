"""
These scripts clean user data csv and convert into records which can be seeded into E12 db.
"""
# standard imports
import datetime

# 3rd party
from django.utils import timezone
import nhs_number
import pandas as pd

# rcpch imports
from epilepsy12.models import (
    Organisation,
    Epilepsy12User,
)
from epilepsy12.tests.factories.E12UserFactory import E12UserFactory
from epilepsy12.constants import (
    AUDIT_CENTRE_LEAD_CLINICIAN,
    VIEW_PREFERENCES,
)
from epilepsy12.common_view_functions.group_for_group import group_for_role


def map_role_name_to_int(_df_role_series):
    """In the current data format, there is only 1 role."""
    role_map = {
        "Audit Centre Lead Clinician": AUDIT_CENTRE_LEAD_CLINICIAN,
    }

    return _df_role_series.map(role_map)


def clean_user_data(csv_path: str = "data.csv") -> list[dict]:
    """Cleans user data and returns records which can be seeded into E12 db."""

    JOINED_DATETIME = datetime.datetime(2023, 11, 24, 0, 0, 0, 0)
    PASSWORD_LAST_SET_GT_90_DAYS = datetime.datetime(2021, 1, 1, 0, 0, 0, 0)

    df = (
        pd.read_csv(csv_path)
        .rename(
            columns={
                "Title": "title",
                "First Name": "first_name",
                "Surname ": "surname",
                "Email": "email",
                "Role": "role",
                "Organisation ODS Code": "organisation_employer_ods_code",
            }
        )
        .drop(
            columns=[
                "Trust",
                "Organisation",
            ]
        )
        .assign(
            role=lambda _df: map_role_name_to_int(_df["role"]),
            last_login=lambda _df: [None] * len(_df),
            date_joined=lambda _df: pd.to_datetime([JOINED_DATETIME] * len(_df)),
            password_last_set=lambda _df: [PASSWORD_LAST_SET_GT_90_DAYS]
            * len(_df),  # FORCES THEM TO CHANGE PASSWORD
        )
    )

    # ORGCODE TYPO FIX
    df["organisation_employer_ods_code"] = df["organisation_employer_ods_code"].replace(
        {"C0X3P": "COX3P"}
    )

    print("CLEANED DATA:")
    print(df.head())
    return df.to_dict(orient="records")


def insert_user_data(csv_path: str = "data.csv"):
    cleaned_records = clean_user_data(csv_path=csv_path)

    already_existing_emails = set(
        Epilepsy12User.objects.all().values_list("email", flat=True)
    )

    users_to_create = []
    seeding_error_report = {}
    total_records = len(cleaned_records)
    for ix, record in enumerate(cleaned_records):
        print("-" * 10, f"On Record {ix} / {total_records-1}", "-" * 10)

        # Duplication check
        if record["email"] in already_existing_emails:
            reason = "Email already exists"
            print(f'Record: {record["email"]} - { reason } - Skipping...')

            seeding_error_report[f"{ix}-INFO-User"] = {
                "reason": f"{record['email']} Record already exists. Skipped.",
                "record": record,
            }
            continue

        # Change to timezone aware datetimes
        password_last_set = timezone.make_aware(record["password_last_set"])
        date_joined = timezone.make_aware(record["date_joined"])

        # Get organisation employer
        try:
            organisation_employer = Organisation.objects.get(
                ods_code=record["organisation_employer_ods_code"]
            )
        except Exception as e:
            print(
                f'Couldn\'t find organisation for {record["organisation_employer_ods_code"]}. Skipping {record["email"]}. Error: {e}'
            )
            seeding_error_report[f"{ix}-ERROR"] = {
                "reason": f"Organisation {record['organisation_employer_ods_code']} could not be found. User {record['email']} was not created.",
                "record": record,
            }
            continue

        new_user = E12UserFactory.build(
            first_name=record["first_name"],
            email=record["email"],
            surname=record["surname"],
            role=record["role"],
            is_active=True, # So they can reset their password
            is_staff=False, # django admin
            is_rcpch_audit_team_member=False,
            is_rcpch_staff=False,
            is_patient_or_carer=False,
            view_preference=VIEW_PREFERENCES[1][0],
            date_joined=date_joined,
            email_confirmed=True,
            password_last_set=password_last_set,
            organisation_employer=organisation_employer,
            groups=[group_for_role(record["role"])],
        )

        users_to_create.append(new_user)
        print("Done!")

    # Gathered all users, now bulk create
    Epilepsy12User.objects.bulk_create(users_to_create)

    # Save all users just to ensure any save methods run
    print(f"{'-'*10}\nSaving all Users to ensure any save methods run\n{'-'*10}")
    total_users_to_save = Epilepsy12User.objects.all().count()
    for ix, user_to_save in enumerate(Epilepsy12User.objects.all()):
        print(f"Saving User {ix+1} of {total_users_to_save}...")
        user_to_save.save()
    print(f"{'-'*10}\nSEEDING ERROR REPORT:\n{'-'*10}")
    print(seeding_error_report)
