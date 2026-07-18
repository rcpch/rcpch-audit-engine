
from datetime import date

"""
Note we are mapping these dates to the audit period fields:
- recruitment_start_date
- recruitment_end_date
- data_collection_end_date
- submission_deadline
These are the keys in the AUDIT_PERIODS dictionary
From cohort 10 onwards we derive these automatically in the management command but from cohort

Cohort Date Rules
Previously (cohorts 4-7) recruitment ran from 1 December to 30 November each year.
The submission deadline was the 2nd Tuesday of the following January.
The period between data collection end and submission deadline is known as the grace period.

Cohort 8 Onwards
The audit team have moved the recruitment dates to coincide with the beginning of every year.
To transition to the new start date, cohort 8 has an extra month of recruitment.
The dates are below. From cohort 10 onwards the dates are automatically derived in the management command.

This function is used in the management command to derive the audit period dates for cohorts below cohort 10.
It is also used in the seed migration 0062.
"""

AUDIT_PERIODS = {
    4:  (date(2020, 12, 1), date(2021, 11, 30), date(2022, 11, 30), date(2023, 1, 10)),
    5:  (date(2021, 12, 1), date(2022, 11, 30), date(2023, 11, 30), date(2024, 1, 9)),
    6:  (date(2022, 12, 1), date(2023, 11, 30), date(2024, 11, 30), date(2025, 1, 14)),
    7:  (date(2023, 12, 1), date(2024, 11, 30), date(2025, 11, 30), date(2026, 1, 13)),
    8:  (date(2024, 12, 1), date(2025, 12, 31), date(2026, 12, 31), date(2027, 1, 12)),
    9:  (date(2026, 1, 1), date(2026, 12, 31), date(2027, 12, 31), date(2028, 1, 11)),
}
