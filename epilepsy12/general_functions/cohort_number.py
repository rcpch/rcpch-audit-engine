"""
Cohort numbers functions
"""

# python imports
from datetime import date

# e12 imports
from .date_functions import nth_tuesday_of_year


def days_remaining_before_submission(audit_submission_date: date) -> int:
    if audit_submission_date:
        remaining_dateime = audit_submission_date - date.today()
        return remaining_dateime.days if remaining_dateime.days > 0 else 0


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

    * Time zone is not explicity supplied. Since this is a UK audit, time zone is assumed always to be UK.

    #### Examples of cohort numbers:
    Cohort 4: 1 December 2020 - 30 November 2021: submission 10 January 2023
    Cohort 5: 1 December 2021 - 30 November 2022: submission 9 January 2024
    Cohort 6: 1 December 2022 - 30 November 2023: submission 14 January 2025
    Cohort 7: 1 December 2023 - 30 November 2024: submission 13 January 2026
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
        audit_submission_date=submission_date
    )

    cohort_data = {
        "cohort": cohort,
        "cohort_start_date": cohort_start_date,
        "cohort_end_date": cohort_end_date,
        "submission_date": submission_date,
        "days_remaining": days_remaining_til_submission,
    }

    return cohort_data
