"""
Cohort numbers functions
"""

# python imports
from datetime import date

# django imports
from django.apps import apps

# e12 imports
from .date_functions import nth_tuesday_of_year


def days_remaining_before_submission(audit_submission_date: date, current_date: date) -> int:
    if audit_submission_date:
        remaining = audit_submission_date - current_date
        # submission is possible on the last day
        return max(0, remaining.days + 1)


def cohort_number_from_first_paediatric_assessment_date(
    first_paediatric_assessment_date: date,
):
    """
    * Returns the cohort number as an `int` from the first paediatric assessment date as a Python `datetime.date`

    * Dates which are too early to return a valid cohort number will return `None`. Ensure to test for a `None` return value before doing anything with the result.

    * Cohort Number is used to identify the groups in the audit by year.

    * Cohorts are defined between 1st December year and 30th November in the subsequent year. Note, the final submission date
    is the second Tuesday in January after the closing date 1 YEAR ON. So if the cohort closes on 30 Nov 22, the submission date is
    the second Tuesday after 30/11/23, which is 9 Jan 24

    Cohorts are defined as follows:
    currently recruiting cohort: this is the cohort that is currently recruiting patients
    currently submitting cohort: this is the cohort that is no longer recruiting patients but is still collecting data to complete a full year of care
    grace cohort: this cohort is also no longer recruiting patients but is still collecting data to complete a full year of care. This cohort is the one before the submitting cohort.

    * Time zone is not explicity supplied. Since this is a UK audit, time zone is assumed always to be UK.

    #### Examples of cohort numbers:
    Cohort 4: 1 December 2020 - 30 November 2021: submission 10 January 2023
    Cohort 5: 1 December 2021 - 30 November 2022: submission 9 January 2024
    Cohort 6: 1 December 2022 - 30 November 2023: submission 14 January 2025
    Cohort 7: 1 December 2023 - 30 November 2024: submission 13 January 2026
    Cohort 8: 1 December 2024 - 30 November 2025: submission 12 January 2027
    """

    if first_paediatric_assessment_date < date(year=2020, month=12, day=1):
        # dates before start of cohort 5 inadmissable
        return None

    if first_paediatric_assessment_date >= date(
        year=first_paediatric_assessment_date.year, month=12, day=1
    ):
        return first_paediatric_assessment_date.year - 2016
    else:
        return (first_paediatric_assessment_date.year - 1) - 2016


def dates_for_cohort(cohort: int):
    """
    Return all dates for cohort numbers
    """

    if cohort is None or cohort < 4:
        return {
            "cohort": None,
            "cohort_start_date": None,
            "cohort_end_date": None,
            "submission_date": None,
            "days_remaining": None,
        }

    cohort_start_date = date(year=2016 + cohort, month=12, day=1)
    cohort_end_date = date(year=2016 + cohort + 1, month=11, day=30)
    submission_date = nth_tuesday_of_year(cohort_end_date.year + 2, n=2)
    days_remaining_til_submission = days_remaining_before_submission(
        audit_submission_date=submission_date,
        current_date=date.today(),
    )

    cohort_data = {
        "cohort": cohort,
        "cohort_start_date": cohort_start_date,
        "cohort_end_date": cohort_end_date,
        "submission_date": submission_date,
        "days_remaining": days_remaining_til_submission,
    }

    return cohort_data


def cohorts_and_dates(first_paediatric_assessment_date: date):
    """
    Returns:
    * currently-recruiting cohort and dates
    * submitting-cohort and dates
    """

    currently_recruiting_cohort_number = (
        cohort_number_from_first_paediatric_assessment_date(
            first_paediatric_assessment_date=first_paediatric_assessment_date
        )
    )

    if currently_recruiting_cohort_number is not None:
        # submitting_cohort_number is always 1 less than currently_recruiting_cohort_number
        submitting_cohort_number = currently_recruiting_cohort_number - 1

        currently_recruiting_cohort = dates_for_cohort(
            cohort=currently_recruiting_cohort_number
        )
        submitting_cohort = dates_for_cohort(cohort=submitting_cohort_number)
    else:
        currently_recruiting_cohort = {}
        submitting_cohort_number = None
        submitting_cohort = {}

    if date.today().month >= 12 or date.today() <= nth_tuesday_of_year(
        date.today().year, n=2
    ):
        # if today is in or after December and before the second Tuesday of the year - during this period
        # a new cohort has started recruiting, the previous cohort has stopped recruiting but is still collecting data
        # and the cohort before that is in the grace period.
        # After the second Tuesday of the year, the grace period cohort is closed, the submitting cohort is closed to recruitment but still collecting data, the currently recruiting cohort is recruiting.

        within_grace_period = True
    else:
        within_grace_period = False

    return {
        "currently_recruiting_cohort": currently_recruiting_cohort_number,
        "currently_recruiting_cohort_start_date": currently_recruiting_cohort.get(
            "cohort_start_date", None
        ),
        "currently_recruiting_cohort_end_date": currently_recruiting_cohort.get(
            "cohort_end_date", None
        ),
        "currently_recruiting_cohort_submission_date": currently_recruiting_cohort.get(
            "submission_date", None
        ),
        "currently_recruiting_cohort_days_remaining": currently_recruiting_cohort.get(
            "days_remaining", None
        ),
        "currently_recruiting_cohort_dates": dates_for_cohort(currently_recruiting_cohort_number),
        "submitting_cohort": submitting_cohort_number,
        "submitting_cohort_start_date": submitting_cohort.get(
            "cohort_start_date", None
        ),
        "submitting_cohort_end_date": submitting_cohort.get("cohort_end_date", None),
        "submitting_cohort_submission_date": submitting_cohort.get(
            "submission_date", None
        ),
        "submitting_cohort_days_remaining": submitting_cohort.get(
            "days_remaining", None
        ),
        "submitting_cohort_dates": dates_for_cohort(submitting_cohort_number),
        "grace_cohort": dates_for_cohort(cohort=submitting_cohort_number - 1),
        "within_grace_period": within_grace_period,
        "today": date.today(),
    }

def get_all_cohort_list():
    """
    Return a list of all cohort numbers starting at 5 (earliest) up to latest cohort in Registration model
    """
    Registration = apps.get_model("epilepsy12", "Registration")
    earliest_cohort = 5
    latest_cohort = Registration.objects.filter().values("cohort").order_by("cohort").last()["cohort"]

    cohort_list = [{'cohort': cohort, 'has_data': Registration.objects.filter(cohort=cohort).exists()} for cohort in range(earliest_cohort, latest_cohort + 1)]
    return cohort_list
