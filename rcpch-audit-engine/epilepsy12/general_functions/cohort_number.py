"""
Cohort numbers functions
"""

from datetime import date


def cohort_number_from_enrolment_date(enrolment_date:date) -> int:
    """
    
    * Cohort Number is used to identify the groups in the audit by year.
    
    * Cohorts are defined between 1st December year and 30th November in the subsequent year.
    
    * Time zone is not explicity supplied. Since this is a UK audit, time zone is assumed always to be UK.

    ## Examples:
        
    Cohort 4: 1 December 2020 - 30 November 2021
    Cohort 5: 1 December 2021 - 30 November 2022
    Cohort 6: 1 December 2022 - 30 November 2023
    Cohort 7: 1 December 2023 - 30 November 2024
    """
    
    for cohort_starting_year in range(2020,2025):
        if enrolment_date >= date(cohort_starting_year, 12, 1) and enrolment_date <= date(cohort_starting_year+1, 11, 30):
            return cohort_starting_year - 2016    
